#!/usr/bin/env python3
"""Phase 4 Batch 4.1: Gold SCD2 and point-in-time join build."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Gold Batch 4.1 SCD2 and PIT tables")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--supplier-history-csv", default="data/reference/supplier_reliability_history.csv")
    parser.add_argument("--route-supplier-csv", default="data/reference/route_supplier_mapping.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    db_path = Path(args.db_path)
    history_csv = Path(args.supplier_history_csv)
    route_csv = Path(args.route_supplier_csv)

    if not db_path.exists():
        raise SystemExit(f"DuckDB file not found: {db_path}. Run previous batches first.")
    if not history_csv.exists():
        raise SystemExit(f"Supplier history CSV not found: {history_csv}")
    if not route_csv.exists():
        raise SystemExit(f"Route-supplier mapping CSV not found: {route_csv}")

    with duckdb.connect(str(db_path)) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS gold")

        silver_count = conn.execute("SELECT count(*) FROM silver.iot_events_curated").fetchone()[0]
        if silver_count == 0:
            raise SystemExit("silver.iot_events_curated has no data. Run Batch 3.2 first.")

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE gold.dim_supplier_reliability_scd2 AS
            WITH base AS (
              SELECT
                supplier_id,
                supplier_name,
                supplier_city,
                CAST(reliability_score AS DOUBLE) AS reliability_score,
                CAST(effective_from AS TIMESTAMP) AS valid_from
              FROM read_csv_auto('{history_csv.as_posix()}', header=true)
            ), versioned AS (
              SELECT
                supplier_id,
                supplier_name,
                supplier_city,
                reliability_score,
                valid_from,
                lead(valid_from) OVER (PARTITION BY supplier_id ORDER BY valid_from) AS next_valid_from
              FROM base
            )
            SELECT
              supplier_id,
              supplier_name,
              supplier_city,
              reliability_score,
              valid_from,
              COALESCE(next_valid_from, TIMESTAMP '9999-12-31 00:00:00') AS valid_to,
              CASE WHEN next_valid_from IS NULL THEN TRUE ELSE FALSE END AS is_current
            FROM versioned
            """
        )

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE gold.dim_route_supplier AS
            SELECT
              route_code,
              supplier_id,
              supplier_name,
              supplier_city
            FROM read_csv_auto('{route_csv.as_posix()}', header=true)
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE gold.fact_iot_events_pit AS
            SELECT
              e.event_ts,
              e.event_date,
              e.sensor_id,
              e.route_code,
              e.origin_city,
              e.destination_city,
              e.origin_ags,
              e.destination_ags,
              e.temperature_c,
              e.humidity_pct,
              e.battery_mv,
              e.vehicle_type,
              e.contract_value_million_eur,
              rs.supplier_id,
              s.supplier_name,
              s.supplier_city,
              s.reliability_score,
              s.valid_from AS supplier_valid_from,
              s.valid_to AS supplier_valid_to,
              s.is_current AS supplier_is_current,
              CASE WHEN e.temperature_c > 8.0 THEN 1 ELSE 0 END AS is_temp_breach,
              current_timestamp AS gold_loaded_at
            FROM silver.iot_events_curated e
            LEFT JOIN gold.dim_route_supplier rs
              ON e.route_code = rs.route_code
            LEFT JOIN gold.dim_supplier_reliability_scd2 s
              ON rs.supplier_id = s.supplier_id
             AND e.event_ts >= s.valid_from
             AND e.event_ts < s.valid_to
            """
        )

        scd2_rows = conn.execute("SELECT count(*) FROM gold.dim_supplier_reliability_scd2").fetchone()[0]
        fact_rows = conn.execute("SELECT count(*) FROM gold.fact_iot_events_pit").fetchone()[0]
        null_supplier = conn.execute(
            "SELECT count(*) FROM gold.fact_iot_events_pit WHERE supplier_id IS NULL"
        ).fetchone()[0]
        overlapping_intervals = conn.execute(
            """
            SELECT count(*)
            FROM gold.dim_supplier_reliability_scd2 a
            JOIN gold.dim_supplier_reliability_scd2 b
              ON a.supplier_id = b.supplier_id
             AND a.valid_from < b.valid_to
             AND b.valid_from < a.valid_to
             AND a.valid_from <> b.valid_from
            """
        ).fetchone()[0]

    print(f"SCD2 rows: {scd2_rows}")
    print(f"Gold fact rows: {fact_rows}")
    print(f"Rows with null supplier_id: {null_supplier}")
    print(f"Overlapping SCD2 intervals: {overlapping_intervals}")

    if null_supplier > 0:
        raise SystemExit("Validation failed: unmatched route->supplier mapping in gold fact")
    if overlapping_intervals > 0:
        raise SystemExit("Validation failed: overlapping SCD2 intervals detected")

    print("Phase 4 Batch 4.1 gold build completed successfully.")


if __name__ == "__main__":
    main()
