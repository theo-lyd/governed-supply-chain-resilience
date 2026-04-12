#!/usr/bin/env python3
"""Phase 6 Batch 6.1: quality gates, freshness checks, and incident logging."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 6.1 operational quality controls")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--default-freshness-hours", type=int, default=6)
    parser.add_argument("--fail-on-breach", action="store_true")
    parser.add_argument(
        "--close-resolved-incidents",
        action="store_true",
        help="Mark matching OPEN incidents as RESOLVED when current checks pass.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    duckdb_errors = (duckdb.Error,)

    db_path = Path(args.db_path)
    if not db_path.exists():
        raise SystemExit(f"DuckDB file not found: {db_path}. Run earlier phases first.")

    freshness_specs = [
        ("bronze.iot_events_raw", "event_ts", args.default_freshness_hours),
        ("silver.iot_events_curated", "event_ts", args.default_freshness_hours),
        ("gold.fact_iot_events_sla", "event_ts", args.default_freshness_hours),
        ("analytics.ml_delay_predictions_baseline", "event_ts", 24),
    ]

    quality_specs = [
        (
            "silver_non_null_route",
            "SELECT count(*) FROM silver.iot_events_curated WHERE route_code IS NULL",
            "Rows with NULL route_code in silver curated table",
        ),
        (
            "gold_non_null_supplier",
            "SELECT count(*) FROM gold.fact_iot_events_sla WHERE supplier_id IS NULL",
            "Rows with NULL supplier_id in gold SLA fact",
        ),
    ]

    with duckdb.connect(str(db_path)) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS ops")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ops.data_freshness_checks (
              table_name VARCHAR,
              ts_column VARCHAR,
              row_count BIGINT,
              max_event_ts TIMESTAMP,
              staleness_hours DOUBLE,
              freshness_threshold_hours INTEGER,
              is_fresh INTEGER,
              check_status VARCHAR,
              checked_at TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ops.quality_gate_results (
              gate_name VARCHAR,
              failed_rows BIGINT,
              gate_status VARCHAR,
              details VARCHAR,
              checked_at TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ops.incident_log (
              incident_id VARCHAR,
              severity VARCHAR,
              status VARCHAR,
              category VARCHAR,
              related_object VARCHAR,
              details VARCHAR,
              detected_at TIMESTAMP,
              resolved_at TIMESTAMP
            )
            """
        )

        conn.execute("DELETE FROM ops.data_freshness_checks")
        conn.execute("DELETE FROM ops.quality_gate_results")

        bronze_cols = {
            row[1]
            for row in conn.execute("PRAGMA table_info('bronze.iot_events_raw')").fetchall()
        }
        has_source_line_number = "source_line_number" in bronze_cols

        quarantine_exists = conn.execute(
            """
            SELECT count(*)
            FROM information_schema.tables
            WHERE table_schema = 'bronze'
              AND table_name = 'iot_events_quarantine'
            """
        ).fetchone()[0] > 0

        if has_source_line_number:
            dup_sql = """
            SELECT count(*)
            FROM (
              SELECT event_ts, sensor_id, route_code, source_file, source_line_number, count(*) AS c
              FROM bronze.iot_events_raw
              GROUP BY 1,2,3,4,5
              HAVING count(*) > 1
            ) d
            """
        else:
            dup_sql = """
            SELECT count(*)
            FROM (
              SELECT event_ts, sensor_id, route_code, source_file, count(*) AS c
              FROM bronze.iot_events_raw
              GROUP BY 1,2,3,4
              HAVING count(*) > 1
            ) d
            """

        quality_specs.extend(
            [
                (
                    "bronze_duplicate_event_key",
                    dup_sql,
                    "Duplicate Bronze event keys",
                ),
                (
                    "bronze_quarantine_volume",
                    "SELECT count(*) FROM bronze.iot_events_quarantine",
                    "Total quarantined Bronze records",
                ),
            ]
        )

        freshness_rows: list[tuple[str, str, int, str, str]] = []
        quality_rows: list[tuple[str, int, str, str]] = []

        for table_name, ts_column, threshold_hours in freshness_specs:
            try:
                row_count, max_ts = conn.execute(
                    f"SELECT count(*), max({ts_column}) FROM {table_name}"
                ).fetchone()
            except duckdb_errors as exc:
                row_count, max_ts = 0, None
                freshness_rows.append((table_name, ts_column, threshold_hours, "FAILED", f"table_or_column_error:{exc}"))
                conn.execute(
                    """
                    INSERT INTO ops.data_freshness_checks
                    VALUES (?, ?, ?, NULL, NULL, ?, 0, 'FAILED', current_timestamp)
                    """,
                    [table_name, ts_column, row_count, threshold_hours],
                )
                continue

            if max_ts is None:
                conn.execute(
                    """
                    INSERT INTO ops.data_freshness_checks
                    VALUES (?, ?, ?, NULL, NULL, ?, 0, 'FAILED', current_timestamp)
                    """,
                    [table_name, ts_column, row_count, threshold_hours],
                )
                freshness_rows.append((table_name, ts_column, threshold_hours, "FAILED", "no_timestamp_data"))
                continue

            staleness_hours = conn.execute("SELECT DATE_DIFF('minute', ?, current_timestamp) / 60.0", [max_ts]).fetchone()[0]
            is_fresh = 1 if staleness_hours <= threshold_hours else 0
            status = "PASS" if is_fresh else "FAILED"
            conn.execute(
                """
                INSERT INTO ops.data_freshness_checks
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, current_timestamp)
                """,
                [table_name, ts_column, row_count, max_ts, staleness_hours, threshold_hours, is_fresh, status],
            )
            freshness_rows.append((table_name, ts_column, threshold_hours, status, f"staleness_hours={staleness_hours:.2f}"))

        for gate_name, sql, details in quality_specs:
            if gate_name == "bronze_quarantine_volume" and not quarantine_exists:
                conn.execute(
                    """
                    INSERT INTO ops.quality_gate_results
                    VALUES (?, 0, 'WARN', ?, current_timestamp)
                    """,
                    [gate_name, "Quarantine table not present yet in this environment"],
                )
                quality_rows.append((gate_name, 0, "WARN", "Quarantine table not present yet in this environment"))
                continue

            try:
                failed_rows = int(conn.execute(sql).fetchone()[0] or 0)
            except duckdb_errors as exc:
                failed_rows = 1
                details = f"{details}; query_error:{exc}"

            if gate_name == "bronze_quarantine_volume":
                status = "WARN" if failed_rows > 0 else "PASS"
            else:
                status = "FAILED" if failed_rows > 0 else "PASS"

            conn.execute(
                """
                INSERT INTO ops.quality_gate_results
                VALUES (?, ?, ?, ?, current_timestamp)
                """,
                [gate_name, failed_rows, status, details],
            )
            quality_rows.append((gate_name, failed_rows, status, details))

        failed_freshness = conn.execute(
            "SELECT count(*) FROM ops.data_freshness_checks WHERE check_status = 'FAILED'"
        ).fetchone()[0]
        failed_quality = conn.execute(
            "SELECT count(*) FROM ops.quality_gate_results WHERE gate_status = 'FAILED'"
        ).fetchone()[0]

        incident_counter = 0
        for table_name, _, _, status, detail in freshness_rows:
            if status != "FAILED":
                continue
            incident_counter += 1
            conn.execute(
                """
                INSERT INTO ops.incident_log
                VALUES (?, 'HIGH', 'OPEN', 'freshness', ?, ?, current_timestamp, NULL)
                """,
                [f"INC-FRESH-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{incident_counter}", table_name, detail],
            )

        for gate_name, failed_rows, status, detail in quality_rows:
            if status != "FAILED":
                continue
            incident_counter += 1
            conn.execute(
                """
                INSERT INTO ops.incident_log
                VALUES (?, 'HIGH', 'OPEN', 'quality_gate', ?, ?, current_timestamp, NULL)
                """,
                [
                    f"INC-QUAL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{incident_counter}",
                    gate_name,
                    f"{detail}; failed_rows={failed_rows}",
                ],
            )

        resolved_incidents = 0
        if args.close_resolved_incidents:
            for table_name, _, _, status, _ in freshness_rows:
                if status != "PASS":
                    continue
                resolved_incidents += conn.execute(
                    """
                    UPDATE ops.incident_log
                    SET status = 'RESOLVED', resolved_at = current_timestamp
                    WHERE status = 'OPEN'
                      AND category = 'freshness'
                      AND related_object = ?
                    """,
                    [table_name],
                ).rowcount

            for gate_name, _, status, _ in quality_rows:
                if status not in {"PASS", "WARN"}:
                    continue
                resolved_incidents += conn.execute(
                    """
                    UPDATE ops.incident_log
                    SET status = 'RESOLVED', resolved_at = current_timestamp
                    WHERE status = 'OPEN'
                      AND category = 'quality_gate'
                      AND related_object = ?
                    """,
                    [gate_name],
                ).rowcount

        open_incidents = conn.execute(
            "SELECT count(*) FROM ops.incident_log WHERE status = 'OPEN'"
        ).fetchone()[0]

    print("Freshness checks:")
    for row in freshness_rows:
        print(row)

    print("Quality gates:")
    for row in quality_rows:
        print(row)

    print(f"Failed freshness checks: {failed_freshness}")
    print(f"Failed quality gates: {failed_quality}")
    if args.close_resolved_incidents:
        print(f"Resolved incidents in this run: {resolved_incidents}")
    print(f"Open incidents: {open_incidents}")

    if args.fail_on_breach and (failed_freshness > 0 or failed_quality > 0):
        raise SystemExit("Phase 6.1 controls failed: freshness or quality gate breaches detected.")

    print("Phase 6 Batch 6.1 controls completed.")


if __name__ == "__main__":
    main()
