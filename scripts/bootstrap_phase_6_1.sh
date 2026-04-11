#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 6.1: Quality Gates, Freshness, and Incident Logging ==="
echo

echo "[1/3] Running Phase 6.1 controls"
python3 scripts/build_ops_phase_6_1.py \
  --db-path data/duckdb/scr.duckdb \
  --default-freshness-hours 6

echo "[2/3] Latest freshness checks"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
rows = conn.execute("""
select table_name, row_count, max_event_ts, staleness_hours, freshness_threshold_hours, check_status
from ops.data_freshness_checks
order by table_name
""").fetchall()
for row in rows:
    print(row)
PY

echo "[3/3] Open incidents"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
rows = conn.execute("""
select incident_id, category, related_object, severity, status, detected_at
from ops.incident_log
where status = 'OPEN'
order by detected_at desc
""").fetchall()
for row in rows:
    print(row)
PY

echo
echo "✅ Batch 6.1 controls completed."
