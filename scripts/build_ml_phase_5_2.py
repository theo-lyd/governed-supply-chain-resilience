#!/usr/bin/env python3
"""Phase 5 Batch 5.2: route clustering and drift-threshold monitoring."""

from __future__ import annotations

import argparse
from pathlib import Path


def kmeans_1d(values: list[float], k: int = 3, max_iter: int = 30) -> tuple[list[int], list[float]]:
    if not values:
        return [], []

    uniq = sorted(set(values))
    if len(uniq) < k:
        k = len(uniq)

    centroids = [uniq[int(i * (len(uniq) - 1) / max(k - 1, 1))] for i in range(k)]

    assignments = [0] * len(values)
    for _ in range(max_iter):
        changed = False

        def nearest_centroid(candidate: float, centroid_values: list[float]) -> int:
            return min(range(k), key=lambda cluster_id: abs(candidate - centroid_values[cluster_id]))

        for idx, value in enumerate(values):
            best = nearest_centroid(value, centroids)
            if assignments[idx] != best:
                assignments[idx] = best
                changed = True

        new_centroids = centroids[:]
        for c in range(k):
            cluster_vals = [v for v, a in zip(values, assignments) if a == c]
            if cluster_vals:
                new_centroids[c] = sum(cluster_vals) / len(cluster_vals)

        centroids = new_centroids
        if not changed:
            break

    return assignments, centroids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 5.2 clustering and drift tables")
    parser.add_argument("--db-path", default="data/duckdb/scr.duckdb")
    parser.add_argument("--score-mean-drift-threshold", type=float, default=0.10)
    parser.add_argument("--positive-rate-drift-threshold", type=float, default=0.15)
    parser.add_argument("--current-window-hours", type=int, default=24)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise SystemExit("duckdb is not installed. Run: pip install duckdb") from exc

    db_path = Path(args.db_path)
    if not db_path.exists():
        raise SystemExit(f"DuckDB file not found: {db_path}. Run earlier batches first.")

    with duckdb.connect(str(db_path)) as conn:
        pred_rows = conn.execute("SELECT count(*) FROM analytics.ml_delay_predictions_baseline").fetchone()[0]
        if pred_rows == 0:
            raise SystemExit("analytics.ml_delay_predictions_baseline has no data. Run Batch 5.1 first.")

        baseline_snapshot = conn.execute(
            """
            SELECT baseline_mean_score, baseline_positive_rate, snapshot_at
            FROM analytics.ml_drift_baseline_snapshots
            WHERE monitor_name = 'drift_monitor_v1'
              AND snapshot_kind = 'train_baseline'
            ORDER BY snapshot_at DESC
            LIMIT 1
            """
        ).fetchone()
        if baseline_snapshot is None:
            raise SystemExit("Missing drift baseline snapshot. Run Batch 5.1 first.")

        conn.execute("CREATE SCHEMA IF NOT EXISTS analytics")

        route_rows = conn.execute(
            """
            SELECT
              route_code,
              AVG(delay_risk_score) AS avg_delay_risk,
              AVG(predicted_delay) AS predicted_delay_rate,
              COUNT(*) AS event_count
            FROM analytics.ml_delay_predictions_baseline
            GROUP BY route_code
            ORDER BY route_code
            """
        ).fetchall()

        route_codes = [r[0] for r in route_rows]
        avg_risks = [float(r[1]) for r in route_rows]
        pred_rates = [float(r[2]) for r in route_rows]
        event_counts = [int(r[3]) for r in route_rows]

        assignments, centroids = kmeans_1d(avg_risks, k=3)
        centroid_order = sorted(range(len(centroids)), key=lambda i: centroids[i])
        rank_map = {cluster_id: rank for rank, cluster_id in enumerate(centroid_order)}

        zone_names = {0: "LOW_RISK_ZONE", 1: "MEDIUM_RISK_ZONE", 2: "HIGH_RISK_ZONE"}

        conn.execute("DROP TABLE IF EXISTS analytics.ml_route_risk_clusters")
        conn.execute(
            """
            CREATE TABLE analytics.ml_route_risk_clusters (
              route_code VARCHAR,
              event_count BIGINT,
              avg_delay_risk DOUBLE,
              predicted_delay_rate DOUBLE,
              cluster_id INTEGER,
              risk_zone VARCHAR,
              cluster_centroid DOUBLE,
              clustered_at TIMESTAMP
            )
            """
        )

        insert_rows = []
        for code, cnt, risk, rate, cluster in zip(route_codes, event_counts, avg_risks, pred_rates, assignments):
            rank = rank_map[cluster]
            zone = zone_names.get(rank, "HIGH_RISK_ZONE")
            centroid = float(centroids[cluster])
            insert_rows.append((code, cnt, risk, rate, int(cluster), zone, centroid))

        conn.executemany(
            """
            INSERT INTO analytics.ml_route_risk_clusters
            (route_code, event_count, avg_delay_risk, predicted_delay_rate, cluster_id, risk_zone, cluster_centroid, clustered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, current_timestamp)
            """,
            insert_rows,
        )

        current = conn.execute(
            f"""
            SELECT
              AVG(delay_risk_score) AS current_mean_score,
              AVG(predicted_delay) AS current_positive_rate,
              COUNT(*) AS current_row_count
            FROM analytics.ml_delay_predictions_baseline
            WHERE data_split = 'eval'
              AND event_ts >= (
                SELECT MAX(event_ts) - INTERVAL '{args.current_window_hours} hours'
                FROM analytics.ml_delay_predictions_baseline
                WHERE data_split = 'eval'
              )
            """
        ).fetchone()

        baseline_mean = float(baseline_snapshot[0] or 0.0)
        baseline_pos = float(baseline_snapshot[1] or 0.0)
        baseline_snapshot_at = baseline_snapshot[2]
        current_mean = float(current[0] or 0.0)
        current_pos = float(current[1] or 0.0)
        current_rows = int(current[2] or 0)

        mean_delta = abs(current_mean - baseline_mean)
        pos_delta = abs(current_pos - baseline_pos)

        mean_breach = 1 if mean_delta > args.score_mean_drift_threshold else 0
        pos_breach = 1 if pos_delta > args.positive_rate_drift_threshold else 0
        overall_breach = 1 if (mean_breach or pos_breach) else 0

        conn.execute("DROP TABLE IF EXISTS analytics.ml_drift_monitoring_status")
        conn.execute(
            """
            CREATE TABLE analytics.ml_drift_monitoring_status AS
            SELECT
              ?::DOUBLE AS baseline_mean_score,
              ?::DOUBLE AS current_mean_score,
              ?::DOUBLE AS mean_score_abs_delta,
              ?::DOUBLE AS mean_score_threshold,
              ?::INTEGER AS mean_score_breach,
              ?::DOUBLE AS baseline_positive_rate,
              ?::DOUBLE AS current_positive_rate,
              ?::DOUBLE AS positive_rate_abs_delta,
              ?::DOUBLE AS positive_rate_threshold,
              ?::INTEGER AS positive_rate_breach,
              ?::INTEGER AS current_eval_row_count,
              ?::TIMESTAMP AS baseline_snapshot_at,
              ?::INTEGER AS overall_drift_breach,
              current_timestamp AS evaluated_at,
              'drift_monitor_v1' AS monitor_name
            """,
            [
                baseline_mean,
                current_mean,
                mean_delta,
                args.score_mean_drift_threshold,
                mean_breach,
                baseline_pos,
                current_pos,
                pos_delta,
                args.positive_rate_drift_threshold,
                pos_breach,
                current_rows,
                baseline_snapshot_at,
                overall_breach,
            ],
        )

        cluster_count = conn.execute("SELECT count(*) FROM analytics.ml_route_risk_clusters").fetchone()[0]
        drift_row = conn.execute(
            """
            SELECT mean_score_abs_delta, positive_rate_abs_delta, overall_drift_breach
            FROM analytics.ml_drift_monitoring_status
            """
        ).fetchone()

    print(f"Route cluster rows: {cluster_count}")
    print(f"Drift deltas (mean_score, positive_rate, breach): {drift_row}")
    print("Phase 5 Batch 5.2 clustering and drift monitoring completed successfully.")


if __name__ == "__main__":
    main()
