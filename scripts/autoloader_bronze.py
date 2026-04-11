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


def read_rows(file_paths: list[str]) -> list[tuple[str, str, str, float, float, int, str]]:
    rows: list[tuple[str, str, str, float, float, int, str]] = []
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as handle:
            for line in handle:
                record = json.loads(line)
                rows.append(
                    (
                        record["event_ts"],
                        record["sensor_id"],
                        record["route_code"],
                        float(record["temperature_c"]),
                        float(record["humidity_pct"]),
                        int(record["battery_mv"]),
                        Path(file_path).name,
                    )
                )
    return rows


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
    rows = read_rows(new_files)

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
              ingested_at TIMESTAMP DEFAULT current_timestamp
            )
            """
        )
        conn.executemany(
            f"""
            INSERT INTO {full_table}
            (event_ts, sensor_id, route_code, temperature_c, humidity_pct, battery_mv, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        total = conn.execute(f"SELECT count(*) FROM {full_table}").fetchone()[0]

    save_state(config.state_file, processed.union(new_files))

    print(f"Loaded {len(rows)} rows from {len(new_files)} new file(s) into {full_table}")
    print(f"Current row_count: {total}")
    print(f"State file updated: {config.state_file}")


if __name__ == "__main__":
    main()
