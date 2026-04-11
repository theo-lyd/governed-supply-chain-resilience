#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 5.1: Baseline Delay-Risk Modeling ==="
echo

echo "[1/4] Verifying Gold SLA baseline"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
count = conn.execute("select count(*) from gold.fact_iot_events_sla").fetchone()[0]
print(f"gold.fact_iot_events_sla row_count: {count}")
if count == 0:
    raise SystemExit("Missing Phase 4 output. Run Batch 4.2 first.")
PY

echo "[2/4] Running Phase 5.1 baseline feature + scoring build"
python3 scripts/build_ml_phase_5_1.py --db-path data/duckdb/scr.duckdb --threshold 0.50

echo "[3/4] Verifying risk score distribution"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select
  min(delay_risk_score) as min_score,
  avg(delay_risk_score) as avg_score,
  max(delay_risk_score) as max_score,
  sum(predicted_delay) as predicted_positive
from analytics.ml_delay_predictions_baseline
""").fetchall())
PY

echo "[4/4] Verifying model metrics"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select model_name, threshold, n, tp, tn, fp, fn, accuracy, precision, recall, f1
from analytics.ml_model_metrics_baseline
""").fetchall())
PY

echo
echo "✅ Batch 5.1 completed. Baseline feature engineering and scoring outputs are ready."
