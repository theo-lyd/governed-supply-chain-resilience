#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="python3"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

FRESHNESS_HOURS="${FRESHNESS_HOURS:-6}"
CLOSE_RESOLVED_INCIDENTS="${CLOSE_RESOLVED_INCIDENTS:-0}"
EXTRA_ARGS=()
if [[ "$CLOSE_RESOLVED_INCIDENTS" == "1" ]]; then
  EXTRA_ARGS+=("--close-resolved-incidents")
fi

echo "=== Batch 6.1: Quality Gates, Freshness, and Incident Logging ==="
echo

echo "[0/3] Ensuring Bronze quarantine table exists"
"$PYTHON_BIN" - << 'PY'
import duckdb

conn = duckdb.connect("data/duckdb/scr.duckdb")
conn.execute("CREATE SCHEMA IF NOT EXISTS bronze")
conn.execute(
    """
    CREATE TABLE IF NOT EXISTS bronze.iot_events_quarantine (
      source_file VARCHAR,
      source_line_number INTEGER,
      raw_record VARCHAR,
      reject_reason VARCHAR,
      rejected_at TIMESTAMP DEFAULT current_timestamp
    )
    """
)
print("bronze.iot_events_quarantine is ready")
PY

echo "[1/3] Running Phase 6.1 controls"
"$PYTHON_BIN" scripts/build_ops_phase_6_1.py \
  --db-path data/duckdb/scr.duckdb \
  --default-freshness-hours "$FRESHNESS_HOURS" \
  "${EXTRA_ARGS[@]}"

echo "[2/3] Latest freshness checks"
"$PYTHON_BIN" - << 'PY'
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
"$PYTHON_BIN" - << 'PY'
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

resolved = conn.execute("""
select count(*)
from ops.incident_log
where status = 'RESOLVED'
  and resolved_at >= current_timestamp - interval '1 hour'
""").fetchone()[0]
print(f"recently_resolved_incidents_last_1h: {resolved}")
PY

echo
echo "✅ Batch 6.1 controls completed."
