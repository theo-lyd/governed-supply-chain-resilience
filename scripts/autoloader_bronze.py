#!/usr/bin/env python3
"""Batch 2.2 incremental ingestion for DuckDB-native track.

This replaces the Databricks cloudFiles Autoloader path with a local incremental
loader that processes only new JSONL files based on a persistent state file.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class IncrementalConfig:
    input_pattern: str
    db_path: str
    schema: str
    table: str
    state_file: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch 2.2 DuckDB incremental ingestion")
    parser.add_argument("--input-pattern", default="data/iot_landing/*.jsonl")
    parser.add_argument("--db-path", default=os.environ.get("DUCKDB_PATH", "data/duckdb/scr.duckdb"))
    parser.add_argument("--schema", default="bronze")
    parser.add_argument("--table", default="iot_events_raw")
    parser.add_argument(
        "--state-file",
        default="data/duckdb/ingestion_state/processed_iot_files.json",
        help="JSON file used to track already ingested input files.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> IncrementalConfig:
    return IncrementalConfig(
        input_pattern=args.input_pattern,
        db_path=args.db_path,
        schema=args.schema,
        table=args.table,
        state_file=args.state_file,
    )


def load_state(path: str) -> set[str]:
    state_path = Path(path)
    if not state_path.exists():
        return set()
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    return set(payload.get("processed_files", []))


def save_state(path: str, processed_files: set[str]) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"processed_files": sorted(processed_files)}, indent=2),
        encoding="utf-8",
    )


def read_rows(
    file_paths: list[str],
) -> tuple[
    list[tuple[str, str, str, float, float, int, str, int]],
    list[tuple[str, int, str, str]],
]:
    rows: list[tuple[str, str, str, float, float, int, str, int]] = []
    rejects: list[tuple[str, int, str, str]] = []
    required = ["event_ts", "sensor_id", "route_code", "temperature_c", "humidity_pct", "battery_mv"]

    for file_path in file_paths:
        source_file = Path(file_path).name
        with open(file_path, "r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                raw_line = line.rstrip("\n")
                try:
                    record = json.loads(raw_line)
                except json.JSONDecodeError:
                    rejects.append((source_file, line_number, raw_line, "malformed_json"))
                    continue

                missing = [k for k in required if k not in record or record[k] in (None, "")]
                if missing:
                    rejects.append((source_file, line_number, raw_line, f"missing_fields:{','.join(missing)}"))
                    continue

                try:
                    rows.append(
                        (
                            str(record["event_ts"]),
                            str(record["sensor_id"]),
                            str(record["route_code"]),
                            float(record["temperature_c"]),
                            float(record["humidity_pct"]),
                            int(record["battery_mv"]),
                            source_file,
                            line_number,
                        )
                    )
                except (TypeError, ValueError):
                    rejects.append((source_file, line_number, raw_line, "invalid_numeric_cast"))

    return rows, rejects


def print_config(config: IncrementalConfig) -> None:
    print(json.dumps(asdict(config), indent=2, sort_keys=True))


def main() -> None:
    args = parse_args()
    config = build_config(args)
    print_config(config)

    candidates = sorted(glob.glob(config.input_pattern))
    processed = load_state(config.state_file)
    new_files = [f for f in candidates if f not in processed]

    print(f"Discovered files: {len(candidates)}")
    print(f"Already processed files: {len(processed)}")
    print(f"New files to ingest: {len(new_files)}")

    if args.dry_run:
        return

    if not new_files:
        print("No new files detected. Nothing to ingest.")
        return

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    Path(config.db_path).parent.mkdir(parents=True, exist_ok=True)
    rows, rejects = read_rows(new_files)

    full_table = f"{config.schema}.{config.table}"
    with duckdb.connect(config.db_path) as conn:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {config.schema}")
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

    save_state(config.state_file, processed.union(new_files))

    print(f"Valid rows parsed: {len(rows)}")
    print(f"Rejected rows quarantined this run: {len(rejects)}")
    print(f"Total quarantined rows: {quarantined}")
    print(f"Loaded deduplicated rows from {len(new_files)} new file(s) into {full_table}")
    print(f"Current row_count: {total}")
    print(f"State file updated: {config.state_file}")


if __name__ == "__main__":
    main()
