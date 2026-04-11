#!/usr/bin/env python3
"""Phase 3 Batch 3.1: build Silver normalized datasets for German constraints.

Creates:
- silver.dim_route_geo: canonical geography by route code with AGS mapping
- silver.iot_events_normalized: bronze events enriched with normalized city names/AGS
"""

from __future__ import annotations

import argparse
from pathlib import Path


CANONICAL_CITY_MAP = {
    "hamburg": "Hamburg",
    "berlin": "Berlin",
    "munchen": "Muenchen",
    "muenchen": "Muenchen",
    "münchen": "Muenchen",
    "koeln": "Koeln",
    "koln": "Koeln",
    "köln": "Koeln",
    "stuttgart": "Stuttgart",
    "frankfurt": "Frankfurt am Main",
    "frankfurt am main": "Frankfurt am Main",
}


def normalize_german_text(value: str | None) -> str | None:
    if value is None:
        return None
    token = " ".join(value.strip().split()).lower()
    return CANONICAL_CITY_MAP.get(token, value.strip())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Silver Batch 3.1 normalization tables")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--mapping-csv", default="data/reference/route_ags_mapping.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    db_path = Path(args.db_path)
    mapping_csv = Path(args.mapping_csv)

    if not mapping_csv.exists():
        raise SystemExit(f"Mapping file not found: {mapping_csv}")

    if not db_path.exists():
        raise SystemExit(f"DuckDB file not found: {db_path}. Run Batch 2.1 first.")

    with duckdb.connect(str(db_path)) as conn:
        conn.create_function("normalize_german_text", normalize_german_text, [str], str)

        conn.execute("CREATE SCHEMA IF NOT EXISTS silver")

        bronze_cols = {
            row[1] for row in conn.execute("PRAGMA table_info('bronze.iot_events_raw')").fetchall()
        }
        if "source_file" not in bronze_cols:
            conn.execute("ALTER TABLE bronze.iot_events_raw ADD COLUMN source_file VARCHAR")

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE silver.dim_route_geo AS
            SELECT
              route_code,
              normalize_german_text(origin_city_raw) AS origin_city,
              normalize_german_text(destination_city_raw) AS destination_city,
              origin_ags,
              destination_ags,
              origin_state,
              destination_state,
              current_timestamp AS normalized_at
            FROM read_csv_auto('{mapping_csv.as_posix()}', header=true)
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE silver.iot_events_normalized AS
            SELECT
              b.event_ts,
              CAST(b.event_ts AS DATE) AS event_date,
              b.sensor_id,
              b.route_code,
              d.origin_city,
              d.destination_city,
              d.origin_ags,
              d.destination_ags,
              b.temperature_c,
              b.humidity_pct,
              b.battery_mv,
              b.source_file,
              b.ingested_at,
              current_timestamp AS silver_loaded_at
            FROM bronze.iot_events_raw b
            LEFT JOIN silver.dim_route_geo d
              ON b.route_code = d.route_code
            """
        )

        missing_routes = conn.execute(
            """
            SELECT count(*)
            FROM (
              SELECT DISTINCT route_code FROM bronze.iot_events_raw
            ) r
            LEFT JOIN silver.dim_route_geo d USING (route_code)
            WHERE d.route_code IS NULL
            """
        ).fetchone()[0]

        null_ags = conn.execute(
            """
            SELECT count(*)
            FROM silver.iot_events_normalized
            WHERE origin_ags IS NULL OR destination_ags IS NULL
            """
        ).fetchone()[0]

        silver_count = conn.execute("SELECT count(*) FROM silver.iot_events_normalized").fetchone()[0]
        dim_count = conn.execute("SELECT count(*) FROM silver.dim_route_geo").fetchone()[0]

    print(f"Built silver.dim_route_geo rows: {dim_count}")
    print(f"Built silver.iot_events_normalized rows: {silver_count}")
    print(f"Missing route mappings: {missing_routes}")
    print(f"Rows with null AGS: {null_ags}")

    if missing_routes > 0:
        raise SystemExit("Validation failed: missing route mappings in silver.dim_route_geo")
    if null_ags > 0:
        raise SystemExit("Validation failed: null AGS values in silver.iot_events_normalized")

    print("Phase 3 Batch 3.1 Silver normalization completed successfully.")


if __name__ == "__main__":
    main()
