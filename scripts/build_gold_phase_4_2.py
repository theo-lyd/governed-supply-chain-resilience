#!/usr/bin/env python3
"""Phase 4 Batch 4.2: event-time SLA breach logic and shipment lead-time marts."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Gold Batch 4.2 SLA and lead-time tables")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--tz-csv", default="data/reference/route_timezone_offsets.csv")
    parser.add_argument("--breach-threshold-c", type=float, default=8.0)
    parser.add_argument("--sustained-breach-minutes", type=int, default=120)
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
            ), ordered AS (
              SELECT
                b.*,
                LAG(event_ts) OVER (PARTITION BY route_code, sensor_id ORDER BY event_ts) AS prev_event_ts,
                LAG(is_temp_breach_flag) OVER (PARTITION BY route_code, sensor_id ORDER BY event_ts) AS prev_is_temp_breach_flag
              FROM base b
            ), streaks AS (
              SELECT
                o.*,
                CASE
                  WHEN o.is_temp_breach_flag = 1 AND COALESCE(o.prev_is_temp_breach_flag, 0) = 1 THEN 0
                  ELSE 1
                END AS new_streak_flag,
                CASE
                  WHEN o.prev_event_ts IS NULL THEN 0
                  ELSE GREATEST(0, DATE_DIFF('minute', o.prev_event_ts, o.event_ts))
                END AS delta_minutes
              FROM ordered o
            ), streak_ids AS (
              SELECT
                s.*,
                SUM(new_streak_flag) OVER (
                  PARTITION BY route_code, sensor_id
                  ORDER BY event_ts
                  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS breach_streak_id
              FROM streaks s
            ), with_durations AS (
              SELECT
                si.*,
                CASE
                  WHEN si.is_temp_breach_flag = 1 THEN
                    SUM(CASE WHEN si.is_temp_breach_flag = 1 THEN si.delta_minutes ELSE 0 END) OVER (
                      PARTITION BY route_code, sensor_id, breach_streak_id
                      ORDER BY event_ts
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    )
                  ELSE 0
                END AS breach_streak_minutes
              FROM streak_ids si
            )
            SELECT
              wd.event_ts,
              wd.event_date,
              wd.sensor_id,
              wd.route_code,
              wd.origin_city,
              wd.destination_city,
              wd.temperature_c,
              wd.humidity_pct,
              wd.battery_mv,
              wd.vehicle_type,
              wd.contract_value_million_eur,
              wd.supplier_id,
              wd.supplier_name,
              wd.reliability_score,
              wd.is_temp_breach,
              wd.is_temp_breach_flag,
              wd.delta_minutes AS event_interval_minutes,
              wd.breach_streak_minutes,
              CASE
                WHEN wd.is_temp_breach_flag = 1 AND wd.breach_streak_minutes >= {args.sustained_breach_minutes} THEN 1
                ELSE 0
              END AS is_sustained_breach,
              tz.origin_tz_offset_hours,
              tz.destination_tz_offset_hours,
              current_timestamp AS gold_sla_loaded_at
            FROM with_durations wd
            LEFT JOIN gold.dim_route_timezone tz
              ON wd.route_code = tz.route_code
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE gold.mart_shipment_lead_time AS
            SELECT
              route_code,
              supplier_id,
              supplier_name,
              sensor_id,
              MIN(event_ts) AS shipment_start_utc,
              MAX(event_ts) AS shipment_end_utc,
              MIN(origin_tz_offset_hours) AS origin_tz_offset_hours,
              MIN(destination_tz_offset_hours) AS destination_tz_offset_hours,
              MIN(event_ts) + (MIN(origin_tz_offset_hours) * INTERVAL '1 hour') AS shipment_start_local,
              MAX(event_ts) + (MIN(destination_tz_offset_hours) * INTERVAL '1 hour') AS shipment_end_local,
              EXTRACT(
                EPOCH FROM (
                  (MAX(event_ts) + (MIN(destination_tz_offset_hours) * INTERVAL '1 hour'))
                  - (MIN(event_ts) + (MIN(origin_tz_offset_hours) * INTERVAL '1 hour'))
                )
              ) / 3600.0 AS shipment_lead_time_hours,
              COUNT(*) AS shipment_event_count,
              MAX(gold_sla_loaded_at) AS latest_loaded_at
            FROM gold.fact_iot_events_sla
            GROUP BY 1,2,3,4
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE gold.mart_route_performance AS
            WITH event_agg AS (
              SELECT
                route_code,
                supplier_id,
                supplier_name,
                COUNT(*) AS event_count,
                AVG(temperature_c) AS avg_temperature_c,
                SUM(is_temp_breach_flag) AS temp_breach_event_count,
                SUM(is_sustained_breach) AS sustained_breach_event_count,
                MAX(gold_sla_loaded_at) AS latest_loaded_at
              FROM gold.fact_iot_events_sla
              GROUP BY 1,2,3
            ), shipment_agg AS (
              SELECT
                route_code,
                supplier_id,
                supplier_name,
                COUNT(*) AS shipment_count,
                AVG(shipment_lead_time_hours) AS avg_shipment_lead_time_hours
              FROM gold.mart_shipment_lead_time
              GROUP BY 1,2,3
            )
            SELECT
              e.route_code,
              e.supplier_id,
              e.supplier_name,
              e.event_count,
              COALESCE(s.shipment_count, 0) AS shipment_count,
              e.avg_temperature_c,
              e.temp_breach_event_count,
              e.sustained_breach_event_count,
              s.avg_shipment_lead_time_hours,
              e.latest_loaded_at
            FROM event_agg e
            LEFT JOIN shipment_agg s
              ON e.route_code = s.route_code
             AND e.supplier_id = s.supplier_id
             AND e.supplier_name = s.supplier_name
            ORDER BY e.route_code
            """
        )

        sla_rows = conn.execute("SELECT count(*) FROM gold.fact_iot_events_sla").fetchone()[0]
        shipment_rows = conn.execute("SELECT count(*) FROM gold.mart_shipment_lead_time").fetchone()[0]
        mart_rows = conn.execute("SELECT count(*) FROM gold.mart_route_performance").fetchone()[0]
        null_tz = conn.execute(
            "SELECT count(*) FROM gold.fact_iot_events_sla WHERE origin_tz_offset_hours IS NULL OR destination_tz_offset_hours IS NULL"
        ).fetchone()[0]
        sustained = conn.execute("SELECT sum(is_sustained_breach) FROM gold.fact_iot_events_sla").fetchone()[0] or 0
        negative_lead = conn.execute(
            "SELECT count(*) FROM gold.mart_shipment_lead_time WHERE shipment_lead_time_hours < 0"
        ).fetchone()[0]

    print(f"SLA fact rows: {sla_rows}")
    print(f"Shipment lead-time rows: {shipment_rows}")
    print(f"Route mart rows: {mart_rows}")
    print(f"Rows with null timezone offsets: {null_tz}")
    print(f"Sustained breach rows (event-time): {sustained}")
    print(f"Shipments with negative lead time: {negative_lead}")

    if null_tz > 0:
        raise SystemExit("Validation failed: missing timezone offsets for one or more routes")
    if negative_lead > 0:
        raise SystemExit("Validation failed: negative shipment lead-time values detected")

    print("Phase 4 Batch 4.2 gold SLA build completed successfully.")


if __name__ == "__main__":
    main()
