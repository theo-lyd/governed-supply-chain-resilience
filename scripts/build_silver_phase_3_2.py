#!/usr/bin/env python3
"""Phase 3 Batch 3.2: incremental lookback and domain normalization.

Builds/refreshes:
- silver.route_business_terms_normalized
- silver.iot_events_curated (lookback refresh window)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def normalize_vehicle_type(value: str | None) -> str | None:
    if value is None:
        return None
    token = value.strip().lower()
    if token in {"lkw", "lkw.", "lkw transport", "lastkraftwagen"}:
        return "LKW"
    return value.strip().upper()


def parse_contract_value_million(value: str | None) -> float | None:
    if value is None:
        return None
    token = value.strip().lower().replace("€", " eur ")
    match = re.search(r"([0-9]+(?:[\.,][0-9]+)?)", token)
    if not match:
        return None

    number = float(match.group(1).replace(",", "."))

    if "mio" in token or "million" in token:
        return number

    if "eur" in token:
        return number / 1_000_000.0

    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Silver Batch 3.2 curated lookback tables")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--terms-csv", default="data/reference/route_business_terms.csv")
    parser.add_argument("--lookback-hours", type=int, default=48)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    db_path = Path(args.db_path)
    terms_csv = Path(args.terms_csv)

    if not db_path.exists():
        raise SystemExit(f"DuckDB file not found: {db_path}. Run earlier batches first.")
    if not terms_csv.exists():
        raise SystemExit(f"Terms mapping file not found: {terms_csv}")

    with duckdb.connect(str(db_path)) as conn:
        conn.create_function("normalize_vehicle_type", normalize_vehicle_type, [str], str)
        conn.create_function("parse_contract_value_million", parse_contract_value_million, [str], float)

        conn.execute("CREATE SCHEMA IF NOT EXISTS silver")

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE silver.route_business_terms_normalized AS
            SELECT
              route_code,
              vehicle_type_raw,
              normalize_vehicle_type(vehicle_type_raw) AS vehicle_type,
              contract_value_raw,
              parse_contract_value_million(contract_value_raw) AS contract_value_million_eur,
              parse_contract_value_million(contract_value_raw) * 1000000 AS contract_value_eur,
              current_timestamp AS normalized_at
            FROM read_csv_auto('{terms_csv.as_posix()}', header=true)
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS silver.iot_events_curated (
              event_ts TIMESTAMP,
              event_date DATE,
              sensor_id VARCHAR,
              route_code VARCHAR,
              origin_city VARCHAR,
              destination_city VARCHAR,
              origin_ags VARCHAR,
              destination_ags VARCHAR,
              temperature_c DOUBLE,
              humidity_pct DOUBLE,
              battery_mv INTEGER,
              source_file VARCHAR,
              ingested_at TIMESTAMP,
              vehicle_type VARCHAR,
              contract_value_million_eur DOUBLE,
              contract_value_eur DOUBLE,
              curated_loaded_at TIMESTAMP
            )
            """
        )

        max_event_ts = conn.execute("SELECT max(event_ts) FROM silver.iot_events_normalized").fetchone()[0]
        if max_event_ts is None:
            raise SystemExit("silver.iot_events_normalized has no data. Run Batch 3.1 first.")

        conn.execute(
            f"""
            DELETE FROM silver.iot_events_curated
            WHERE event_ts >= (
              TIMESTAMP '{max_event_ts}' - INTERVAL '{args.lookback_hours} hours'
            )
            """
        )

        conn.execute(
            f"""
            INSERT INTO silver.iot_events_curated
            SELECT
              n.event_ts,
              n.event_date,
              n.sensor_id,
              n.route_code,
              n.origin_city,
              n.destination_city,
              n.origin_ags,
              n.destination_ags,
              n.temperature_c,
              n.humidity_pct,
              n.battery_mv,
              n.source_file,
              n.ingested_at,
              t.vehicle_type,
              t.contract_value_million_eur,
              t.contract_value_eur,
              current_timestamp AS curated_loaded_at
            FROM silver.iot_events_normalized n
            LEFT JOIN silver.route_business_terms_normalized t
              ON n.route_code = t.route_code
            WHERE n.event_ts >= (
              TIMESTAMP '{max_event_ts}' - INTERVAL '{args.lookback_hours} hours'
            )
            """
        )

        lookback_source_count = conn.execute(
            f"""
            SELECT count(*) FROM silver.iot_events_normalized
            WHERE event_ts >= (
              TIMESTAMP '{max_event_ts}' - INTERVAL '{args.lookback_hours} hours'
            )
            """
        ).fetchone()[0]

        curated_count = conn.execute("SELECT count(*) FROM silver.iot_events_curated").fetchone()[0]
        null_vehicle = conn.execute(
            "SELECT count(*) FROM silver.iot_events_curated WHERE vehicle_type IS NULL"
        ).fetchone()[0]
        null_contract = conn.execute(
            "SELECT count(*) FROM silver.iot_events_curated WHERE contract_value_million_eur IS NULL"
        ).fetchone()[0]

    print(f"Lookback source rows: {lookback_source_count}")
    print(f"Curated table total rows: {curated_count}")
    print(f"Rows with null vehicle_type: {null_vehicle}")
    print(f"Rows with null contract_value_million_eur: {null_contract}")

    if null_vehicle > 0:
        raise SystemExit("Validation failed: vehicle_type normalization has nulls")
    if null_contract > 0:
        raise SystemExit("Validation failed: contract_value normalization has nulls")

    print("Phase 3 Batch 3.2 curated lookback build completed successfully.")


if __name__ == "__main__":
    main()
