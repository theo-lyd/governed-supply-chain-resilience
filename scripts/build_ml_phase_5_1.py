#!/usr/bin/env python3
"""Phase 5 Batch 5.1: temporal baseline features, scoring, and evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 5.1 baseline ML features and scores")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--threshold", type=float, default=0.50)
    parser.add_argument("--eval-window-hours", type=int, default=24)
    parser.add_argument("--target-horizon-hours", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    db_path = Path(args.db_path)
    if not db_path.exists():
        raise SystemExit(f"DuckDB file not found: {db_path}. Run earlier phases first.")

    with duckdb.connect(str(db_path)) as conn:
        base_rows = conn.execute("SELECT count(*) FROM gold.fact_iot_events_sla").fetchone()[0]
        if base_rows == 0:
            raise SystemExit("gold.fact_iot_events_sla has no data. Run Batch 4.2 first.")

        conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")

        conn.execute(
            f"""
            CREATE OR REPLACE TABLE analytics.ml_features_delay_baseline AS
            WITH cutoff AS (
              SELECT MAX(event_ts) - INTERVAL '{args.eval_window_hours} hours' AS eval_start_ts
              FROM gold.fact_iot_events_sla
            )
            SELECT
              f.event_ts,
              f.event_date,
              f.route_code,
              f.sensor_id,
              f.supplier_id,
              f.supplier_name,
              f.reliability_score,
              f.temperature_c,
              f.humidity_pct,
              f.battery_mv,
              f.contract_value_million_eur,
              f.is_temp_breach_flag,
              f.breach_streak_minutes,
              CASE WHEN f.event_ts < c.eval_start_ts THEN 'train' ELSE 'eval' END AS data_split,
              CASE
                WHEN EXISTS (
                  SELECT 1
                  FROM gold.fact_iot_events_sla f2
                  WHERE f2.route_code = f.route_code
                    AND f2.sensor_id = f.sensor_id
                    AND f2.event_ts > f.event_ts
                    AND f2.event_ts <= f.event_ts + INTERVAL '{args.target_horizon_hours} hours'
                    AND f2.is_sustained_breach = 1
                ) THEN 1
                ELSE 0
              END AS delay_label_future_horizon
            FROM gold.fact_iot_events_sla f
            CROSS JOIN cutoff c
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE analytics.ml_delay_predictions_baseline AS
            WITH scored AS (
              SELECT
                *,
                LEAST(
                  1.0,
                  GREATEST(
                    0.0,
                    0.10
                    + (CASE WHEN is_temp_breach_flag = 1 THEN 0.22 ELSE 0.0 END)
                    + (LEAST(180.0, GREATEST(0.0, breach_streak_minutes)) * 0.0015)
                    + (GREATEST(0.0, 90.0 - reliability_score) * 0.01)
                    + (GREATEST(0.0, contract_value_million_eur - 1.0) * 0.02)
                  )
                ) AS delay_risk_score
              FROM analytics.ml_features_delay_baseline
            )
            SELECT
              scored.*,
              CASE WHEN delay_risk_score >= ? THEN 1 ELSE 0 END AS predicted_delay
            FROM scored
            """,
            [args.threshold],
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE analytics.ml_model_metrics_baseline AS
            WITH cm AS (
              SELECT
                data_split,
                SUM(CASE WHEN delay_label_future_horizon = 1 AND predicted_delay = 1 THEN 1 ELSE 0 END) AS tp,
                SUM(CASE WHEN delay_label_future_horizon = 0 AND predicted_delay = 0 THEN 1 ELSE 0 END) AS tn,
                SUM(CASE WHEN delay_label_future_horizon = 0 AND predicted_delay = 1 THEN 1 ELSE 0 END) AS fp,
                SUM(CASE WHEN delay_label_future_horizon = 1 AND predicted_delay = 0 THEN 1 ELSE 0 END) AS fn,
                COUNT(*) AS n
              FROM analytics.ml_delay_predictions_baseline
              GROUP BY data_split
            )
            SELECT
              data_split,
              tp,
              tn,
              fp,
              fn,
              n,
              (tp + tn) * 1.0 / NULLIF(n, 0) AS accuracy,
              tp * 1.0 / NULLIF(tp + fp, 0) AS precision,
              tp * 1.0 / NULLIF(tp + fn, 0) AS recall,
              2.0 * (tp * 1.0 / NULLIF(tp + fp, 0)) * (tp * 1.0 / NULLIF(tp + fn, 0))
                / NULLIF((tp * 1.0 / NULLIF(tp + fp, 0)) + (tp * 1.0 / NULLIF(tp + fn, 0)), 0) AS f1,
              current_timestamp AS evaluated_at,
              'baseline_rule_weighted_v2_temporal_split' AS model_name,
              ?::DOUBLE AS threshold
            FROM cm
            ORDER BY data_split
            """,
            [args.threshold],
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analytics.ml_drift_baseline_snapshots (
              monitor_name VARCHAR,
              snapshot_kind VARCHAR,
              baseline_mean_score DOUBLE,
              baseline_positive_rate DOUBLE,
              baseline_row_count BIGINT,
              model_name VARCHAR,
              threshold DOUBLE,
              snapshot_at TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            INSERT INTO analytics.ml_drift_baseline_snapshots
            SELECT
              'drift_monitor_v1' AS monitor_name,
              'train_baseline' AS snapshot_kind,
              AVG(delay_risk_score) AS baseline_mean_score,
              AVG(predicted_delay) AS baseline_positive_rate,
              COUNT(*) AS baseline_row_count,
              'baseline_rule_weighted_v2_temporal_split' AS model_name,
              ?::DOUBLE AS threshold,
              current_timestamp AS snapshot_at
            FROM analytics.ml_delay_predictions_baseline
            WHERE data_split = 'train'
            """,
            [args.threshold],
        )

        feature_rows = conn.execute("SELECT count(*) FROM analytics.ml_features_delay_baseline").fetchone()[0]
        pred_rows = conn.execute("SELECT count(*) FROM analytics.ml_delay_predictions_baseline").fetchone()[0]
        metrics = conn.execute(
            """
            SELECT data_split, n, tp, tn, fp, fn, accuracy, precision, recall, f1
            FROM analytics.ml_model_metrics_baseline
            ORDER BY data_split
            """
        ).fetchall()

    print(f"Feature rows: {feature_rows}")
    print(f"Prediction rows: {pred_rows}")
    print("Metrics by split (split, n, tp, tn, fp, fn, acc, prec, rec, f1):")
    for row in metrics:
        print(row)
    print("Phase 5 Batch 5.1 temporal model pipeline completed successfully.")


if __name__ == "__main__":
    main()
