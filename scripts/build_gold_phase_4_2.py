#!/usr/bin/env python3
"""Phase 4 Batch 4.2: rolling breach logic and timezone-safe lead-time metrics."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Gold Batch 4.2 SLA and lead-time tables")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--tz-csv", default="data/reference/route_timezone_offsets.csv")
    parser.add_argument("--breach-threshold-c", type=float, default=8.0)
    parser.add_argument("--rolling-window-rows", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    db_path = Path(args.db_path)
    tz_csv = Path(args.tz_csv)

    if not db_path.exists():
        raise SystemExit(f"DuckDB file not found: {db_path}. Run previous batches first.")
    if not tz_csv.exists():
        raise SystemExit(f"Timezone mapping CSV not found: {tz_csv}")

    with duckdb.connect(str(db_path)) as conn:
        fact_rows = conn.execute("SELECT count(*) FROM gold.fact_iot_events_pit").fetchone()[0]
        if fact_rows == 0:
            raise SystemExit("gold.fact_iot_events_pit has no data. Run Batch 4.1 first.")

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE gold.dim_route_timezone AS
            SELECT
              route_code,
              CAST(origin_tz_offset_hours AS INTEGER) AS origin_tz_offset_hours,
              CAST(destination_tz_offset_hours AS INTEGER) AS destination_tz_offset_hours
            FROM read_csv_auto('{tz_csv.as_posix()}', header=true)
            """
        )

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE gold.fact_iot_events_sla AS
            WITH base AS (
              SELECT
                f.*,
                CASE WHEN f.temperature_c > {args.breach_threshold_c} THEN 1 ELSE 0 END AS is_temp_breach_flag
              FROM gold.fact_iot_events_pit f
            ), rolling AS (
              SELECT
                base.*,
                SUM(is_temp_breach_flag) OVER (
                  PARTITION BY route_code
                  ORDER BY event_ts
                  ROWS BETWEEN {args.rolling_window_rows - 1} PRECEDING AND CURRENT ROW
                ) AS rolling_breach_count
              FROM base
            )
            SELECT
              rolling.event_ts,
              rolling.event_date,
              rolling.sensor_id,
              rolling.route_code,
              rolling.origin_city,
              rolling.destination_city,
              rolling.temperature_c,
              rolling.humidity_pct,
              rolling.battery_mv,
              rolling.vehicle_type,
              rolling.contract_value_million_eur,
              rolling.supplier_id,
              rolling.supplier_name,
              rolling.reliability_score,
              rolling.is_temp_breach,
              rolling.is_temp_breach_flag,
              rolling.rolling_breach_count,
              CASE WHEN rolling.rolling_breach_count >= {args.rolling_window_rows} THEN 1 ELSE 0 END AS is_sustained_breach,
              tz.origin_tz_offset_hours,
              tz.destination_tz_offset_hours,
              current_timestamp AS gold_sla_loaded_at
            FROM rolling
            LEFT JOIN gold.dim_route_timezone tz
              ON rolling.route_code = tz.route_code
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE gold.mart_route_performance AS
            SELECT
              route_code,
              supplier_id,
              supplier_name,
              count(*) AS event_count,
              avg(temperature_c) AS avg_temperature_c,
              sum(is_temp_breach_flag) AS temp_breach_event_count,
              sum(is_sustained_breach) AS sustained_breach_event_count,
              avg(
                (
                  EXTRACT(EPOCH FROM (event_ts + (destination_tz_offset_hours * INTERVAL '1 hour')
                    - (event_ts + (origin_tz_offset_hours * INTERVAL '1 hour'))))
                ) / 3600.0
              ) AS tz_safe_lead_time_hours,
              max(gold_sla_loaded_at) AS latest_loaded_at
            FROM gold.fact_iot_events_sla
            GROUP BY 1,2,3
            ORDER BY route_code
            """
        )

        sla_rows = conn.execute("SELECT count(*) FROM gold.fact_iot_events_sla").fetchone()[0]
        mart_rows = conn.execute("SELECT count(*) FROM gold.mart_route_performance").fetchone()[0]
        null_tz = conn.execute(
            "SELECT count(*) FROM gold.fact_iot_events_sla WHERE origin_tz_offset_hours IS NULL OR destination_tz_offset_hours IS NULL"
        ).fetchone()[0]
        sustained = conn.execute("SELECT sum(is_sustained_breach) FROM gold.fact_iot_events_sla").fetchone()[0] or 0

    print(f"SLA fact rows: {sla_rows}")
    print(f"Route mart rows: {mart_rows}")
    print(f"Rows with null timezone offsets: {null_tz}")
    print(f"Sustained breach rows: {sustained}")

    if null_tz > 0:
        raise SystemExit("Validation failed: missing timezone offsets for one or more routes")

    print("Phase 4 Batch 4.2 gold SLA build completed successfully.")


if __name__ == "__main__":
    main()
