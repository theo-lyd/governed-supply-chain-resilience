#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 5.2: Route Clustering and Drift Monitoring ==="
echo

echo "[1/4] Verifying Batch 5.1 baseline outputs"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
count = conn.execute("select count(*) from analytics.ml_delay_predictions_baseline").fetchone()[0]
print(f"analytics.ml_delay_predictions_baseline row_count: {count}")
if count == 0:
    raise SystemExit("Missing Batch 5.1 output. Run Batch 5.1 first.")
PY

echo "[2/4] Running Batch 5.2 clustering + drift monitoring"
python3 scripts/build_ml_phase_5_2.py \
  --db-path data/duckdb/scr.duckdb \
  --score-mean-drift-threshold 0.10 \
  --positive-rate-drift-threshold 0.15

echo "[3/4] Verifying route risk clusters"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
rows = conn.execute("""
select route_code, event_count, avg_delay_risk, predicted_delay_rate, risk_zone
from analytics.ml_route_risk_clusters
order by avg_delay_risk desc
""").fetchall()
for row in rows:
    print(row)
PY

echo "[4/4] Verifying drift monitoring status"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select monitor_name, mean_score_abs_delta, positive_rate_abs_delta, overall_drift_breach, evaluated_at
from analytics.ml_drift_monitoring_status
""").fetchall())
PY

echo
echo "✅ Batch 5.2 completed. Clustering and drift monitoring artifacts are ready."
