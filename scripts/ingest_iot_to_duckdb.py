#!/usr/bin/env python3
"""Load local IoT JSONL files into a DuckDB Bronze table with quarantine + dedup."""

import argparse
import glob
import json
from pathlib import Path


def load_rows(
    pattern: str,
) -> tuple[
    list[tuple[str, str, str, float, float, int, str, int]],
    list[tuple[str, int, str, str]],
]:
    rows: list[tuple[str, str, str, float, float, int, str, int]] = []
    rejects: list[tuple[str, int, str, str]] = []
    required = ["event_ts", "sensor_id", "route_code", "temperature_c", "humidity_pct", "battery_mv"]

    for file_path in sorted(glob.glob(pattern)):
        source_file = Path(file_path).name
        with open(file_path, "r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                raw_line = line.rstrip("\n")
                try:
                    payload = json.loads(raw_line)
                except json.JSONDecodeError:
                    rejects.append((source_file, line_number, raw_line, "malformed_json"))
                    continue

                missing = [k for k in required if k not in payload or payload[k] in (None, "")]
                if missing:
                    rejects.append((source_file, line_number, raw_line, f"missing_fields:{','.join(missing)}"))
                    continue

                try:
                    rows.append(
                        (
                            str(payload["event_ts"]),
                            str(payload["sensor_id"]),
                            str(payload["route_code"]),
                            float(payload["temperature_c"]),
                            float(payload["humidity_pct"]),
                            int(payload["battery_mv"]),
                            source_file,
                            line_number,
                        )
                    )
                except (TypeError, ValueError):
                    rejects.append((source_file, line_number, raw_line, "invalid_numeric_cast"))

    return rows, rejects


def main() -> None:
    parser = argparse.ArgumentParser(description="Load IoT JSONL files into DuckDB Bronze table")
    parser.add_argument("--input-pattern", default="data/iot_landing/*.jsonl")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--schema", default="bronze")
    parser.add_argument("--table", default="iot_events_raw")
    args = parser.parse_args()

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    rows, rejects = load_rows(args.input_pattern)
    if not rows and not rejects:
        raise SystemExit(f"No records found for pattern: {args.input_pattern}")

    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    full_table = f"{args.schema}.{args.table}"

    with duckdb.connect(str(db_path)) as conn:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {args.schema}")
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {full_table} (
              event_ts TIMESTAMP,
              sensor_id VARCHAR,
              route_code VARCHAR,
              temperature_c DOUBLE,
              humidity_pct DOUBLE,
              battery_mv INTEGER,
              source_file VARCHAR,
              source_line_number INTEGER,
              ingested_at TIMESTAMP DEFAULT current_timestamp
            )
            """
        )

        existing_cols = {r[1] for r in conn.execute(f"PRAGMA table_info('{full_table}')").fetchall()}
        if "source_file" not in existing_cols:
            conn.execute(f"ALTER TABLE {full_table} ADD COLUMN source_file VARCHAR")
        if "source_line_number" not in existing_cols:
            conn.execute(f"ALTER TABLE {full_table} ADD COLUMN source_line_number INTEGER")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bronze.iot_events_quarantine (
              source_file VARCHAR,
              source_line_number INTEGER,
              raw_record VARCHAR,
              reject_reason VARCHAR,
              rejected_at TIMESTAMP DEFAULT current_timestamp
            )
            """
        )

        if rejects:
            conn.executemany(
                """
                INSERT INTO bronze.iot_events_quarantine
                (source_file, source_line_number, raw_record, reject_reason)
                VALUES (?, ?, ?, ?)
                """,
                rejects,
            )

        if rows:
            conn.execute("DROP TABLE IF EXISTS temp_bronze_iot_stage")
            conn.execute(
                """
                CREATE TEMP TABLE temp_bronze_iot_stage (
                  event_ts TIMESTAMP,
                  sensor_id VARCHAR,
                  route_code VARCHAR,
                  temperature_c DOUBLE,
                  humidity_pct DOUBLE,
                  battery_mv INTEGER,
                  source_file VARCHAR,
                  source_line_number INTEGER
                )
                """
            )
            conn.executemany(
                """
                INSERT INTO temp_bronze_iot_stage
                (event_ts, sensor_id, route_code, temperature_c, humidity_pct, battery_mv, source_file, source_line_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.execute(
                f"""
                INSERT INTO {full_table}
                (event_ts, sensor_id, route_code, temperature_c, humidity_pct, battery_mv, source_file, source_line_number)
                SELECT
                  s.event_ts,
                  s.sensor_id,
                  s.route_code,
                  s.temperature_c,
                  s.humidity_pct,
                  s.battery_mv,
                  s.source_file,
                  s.source_line_number
                FROM temp_bronze_iot_stage s
                LEFT JOIN {full_table} t
                  ON t.event_ts = s.event_ts
                 AND t.sensor_id = s.sensor_id
                 AND t.route_code = s.route_code
                 AND COALESCE(t.source_file, '') = COALESCE(s.source_file, '')
                 AND COALESCE(t.source_line_number, -1) = COALESCE(s.source_line_number, -1)
                WHERE t.sensor_id IS NULL
                """
            )

        total = conn.execute(f"SELECT count(*) FROM {full_table}").fetchone()[0]
        quarantined = conn.execute("SELECT count(*) FROM bronze.iot_events_quarantine").fetchone()[0]

    print(f"Valid rows parsed: {len(rows)}")
    print(f"Rejected rows quarantined this run: {len(rejects)}")
    print(f"Total quarantined rows: {quarantined}")
    print(f"Current row_count: {total}")
    print(f"DuckDB file: {db_path}")


if __name__ == "__main__":
    main()
