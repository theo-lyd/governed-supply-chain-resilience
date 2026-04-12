#!/usr/bin/env python3
"""Compatibility Bronze loader for the DuckDB-native execution track.

This preserves the historical command name while removing Databricks runtime
coupling from the active repository path.
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path


def load_rows(pattern: str) -> list[tuple[str, str, str, float, float, int, str]]:
    rows: list[tuple[str, str, str, float, float, int, str]] = []
    for file_path in sorted(glob.glob(pattern)):
        with open(file_path, "r", encoding="utf-8") as handle:
            for line in handle:
                payload = json.loads(line)
                rows.append(
                    (
                        payload["event_ts"],
                        payload["sensor_id"],
                        payload["route_code"],
                        float(payload["temperature_c"]),
                        float(payload["humidity_pct"]),
                        int(payload["battery_mv"]),
                        Path(file_path).name,
                    )
                )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load local IoT JSONL files into DuckDB Bronze table."
    )
    parser.add_argument("--input-pattern", default="data/iot_landing/*.jsonl")
    parser.add_argument(
        "--catalog",
        default=None,
        help="Deprecated and ignored; retained for backward compatibility.",
    )
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--schema", default="bronze")
    parser.add_argument("--table", default="iot_events_raw")
    args = parser.parse_args()

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    rows = load_rows(args.input_pattern)
    if not rows:
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
              ingested_at TIMESTAMP DEFAULT current_timestamp
            )
            """
        )

        existing_cols = {
            row[1] for row in conn.execute(f"PRAGMA table_info('{full_table}')").fetchall()
        }
        if "source_file" not in existing_cols:
            conn.execute(f"ALTER TABLE {full_table} ADD COLUMN source_file VARCHAR")

        conn.executemany(
            f"""
            INSERT INTO {full_table}
            (event_ts, sensor_id, route_code, temperature_c, humidity_pct, battery_mv, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        total = conn.execute(f"SELECT count(*) FROM {full_table}").fetchone()[0]

    if args.catalog:
        print("Deprecated --catalog argument was ignored; DuckDB stores data locally.")
    print(f"Loaded {len(rows)} rows into {full_table}")
    print(f"Current row_count: {total}")


if __name__ == "__main__":
    main()
