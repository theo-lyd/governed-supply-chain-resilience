#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 4.2: Rolling Breach and Timezone-Safe Lead Time ==="
echo

echo "[1/4] Verifying Batch 4.1 Gold baseline"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
count = conn.execute("select count(*) from gold.fact_iot_events_pit").fetchone()[0]
print(f"gold.fact_iot_events_pit row_count: {count}")
if count == 0:
    raise SystemExit("Missing Batch 4.1 output. Run Batch 4.1 first.")
PY

echo "[2/4] Running Batch 4.2 gold build"
python3 scripts/build_gold_phase_4_2.py \
  --db-path data/duckdb/scr.duckdb \
  --tz-csv data/reference/route_timezone_offsets.csv \
  --breach-threshold-c 8.0 \
  --sustained-breach-minutes 120

echo "[3/4] Verifying SLA flags"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select route_code,
       sum(is_temp_breach_flag) as breach_events,
       sum(is_sustained_breach) as sustained_events
from gold.fact_iot_events_sla
group by 1
order by 1
""").fetchall())
PY

echo "[4/4] Verifying timezone-safe lead-time mart"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
rows = conn.execute("""
select route_code, supplier_id, event_count, shipment_count, avg_shipment_lead_time_hours
from gold.mart_route_performance
order by route_code
""").fetchall()
for row in rows:
    print(row)
PY

echo
echo "✅ Batch 4.2 completed. SLA and lead-time marts are ready."
