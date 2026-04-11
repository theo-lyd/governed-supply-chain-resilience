# Phase 5 Commands

This log captures commands for Batch 5.1 (baseline delay-risk feature engineering and scoring).

## Chunk 1: Input Baseline Checks

### Verify Gold SLA baseline exists
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("select count(*) from gold.fact_iot_events_sla").fetchone()[0])
PY
```

## Chunk 2: Batch 5.1 Execution

### One-command bootstrap
```bash
chmod +x ./scripts/bootstrap_phase_5_1.sh
./scripts/bootstrap_phase_5_1.sh
```

### Direct build command
```bash
python3 scripts/build_ml_phase_5_1.py --db-path data/duckdb/scr.duckdb --threshold 0.50
```

## Chunk 3: Validation Queries

### Score distribution checks
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select min(delay_risk_score), avg(delay_risk_score), max(delay_risk_score), sum(predicted_delay)
from analytics.ml_delay_predictions_baseline
""").fetchall())
PY
```

### Baseline metric checks
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select model_name, threshold, n, tp, tn, fp, fn, accuracy, precision, recall, f1
from analytics.ml_model_metrics_baseline
""").fetchall())
PY
```

## Notes
- Batch 5.1 implements BL-019 and BL-020 baseline scope for reproducible features and delay-risk scoring.
- Batch 5.2 will add clustering and model drift monitoring thresholds.

## Batch 5.2: Route Clustering + Drift Threshold Monitoring

### One-command bootstrap
```bash
chmod +x ./scripts/bootstrap_phase_5_2.sh
./scripts/bootstrap_phase_5_2.sh
```

### Direct build command
```bash
python3 scripts/build_ml_phase_5_2.py \
	--db-path data/duckdb/scr.duckdb \
	--score-mean-drift-threshold 0.10 \
	--positive-rate-drift-threshold 0.15
```

### Validate route clustering output
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select route_code, event_count, avg_delay_risk, predicted_delay_rate, risk_zone
from analytics.ml_route_risk_clusters
order by avg_delay_risk desc
""").fetchall())
PY
```

### Validate drift monitoring status
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select monitor_name, mean_score_abs_delta, positive_rate_abs_delta, overall_drift_breach
from analytics.ml_drift_monitoring_status
""").fetchall())
PY
```

## Updated Notes
- Batch 5.1 implements BL-019 and BL-020 baseline scope.
- Batch 5.2 implements BL-021 (route clustering) and BL-022 (drift thresholds and monitoring status).
