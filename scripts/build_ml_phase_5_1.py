#!/usr/bin/env python3
"""Phase 5 Batch 5.1: baseline delay-risk feature engineering and scoring."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 5.1 baseline ML features and scores")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--threshold", type=float, default=0.50)
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
            """
            CREATE OR REPLACE TABLE analytics.ml_features_delay_baseline AS
            SELECT
              event_ts,
              event_date,
              route_code,
              supplier_id,
              supplier_name,
              reliability_score,
              temperature_c,
              humidity_pct,
              battery_mv,
              is_temp_breach_flag,
              is_sustained_breach,
              rolling_breach_count,
              contract_value_million_eur,
              -- Binary label proxy for baseline supervised setup.
              CASE
                WHEN is_sustained_breach = 1 THEN 1
                WHEN is_temp_breach_flag = 1 AND reliability_score < 88 THEN 1
                ELSE 0
              END AS delay_label
            FROM gold.fact_iot_events_sla
            """
        )

        conn.execute(
            """
            CREATE OR REPLACE TABLE analytics.ml_delay_predictions_baseline AS
            WITH scored AS (
              SELECT
                *,
                -- Weighted baseline risk score in [0,1].
                LEAST(
                  1.0,
                  GREATEST(
                    0.0,
                    0.15
                    + (CASE WHEN is_temp_breach_flag = 1 THEN 0.30 ELSE 0.0 END)
                    + (CASE WHEN is_sustained_breach = 1 THEN 0.35 ELSE 0.0 END)
                    + (LEAST(5.0, GREATEST(0.0, rolling_breach_count)) * 0.04)
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
                SUM(CASE WHEN delay_label = 1 AND predicted_delay = 1 THEN 1 ELSE 0 END) AS tp,
                SUM(CASE WHEN delay_label = 0 AND predicted_delay = 0 THEN 1 ELSE 0 END) AS tn,
                SUM(CASE WHEN delay_label = 0 AND predicted_delay = 1 THEN 1 ELSE 0 END) AS fp,
                SUM(CASE WHEN delay_label = 1 AND predicted_delay = 0 THEN 1 ELSE 0 END) AS fn,
                COUNT(*) AS n
              FROM analytics.ml_delay_predictions_baseline
            )
            SELECT
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
              'baseline_rule_weighted_v1' AS model_name,
              ?::DOUBLE AS threshold
            FROM cm
            """,
            [args.threshold],
        )

        feature_rows = conn.execute("SELECT count(*) FROM analytics.ml_features_delay_baseline").fetchone()[0]
        pred_rows = conn.execute("SELECT count(*) FROM analytics.ml_delay_predictions_baseline").fetchone()[0]
        metrics = conn.execute(
            "SELECT n, tp, tn, fp, fn, accuracy, precision, recall, f1 FROM analytics.ml_model_metrics_baseline"
        ).fetchone()

    print(f"Feature rows: {feature_rows}")
    print(f"Prediction rows: {pred_rows}")
    print(
        "Metrics n/tp/tn/fp/fn/accuracy/precision/recall/f1:",
        metrics,
    )
    print("Phase 5 Batch 5.1 baseline model pipeline completed successfully.")


if __name__ == "__main__":
    main()
