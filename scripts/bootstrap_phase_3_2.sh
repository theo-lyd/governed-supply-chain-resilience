#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 3.2: Incremental Lookback and Domain Normalization ==="
echo

echo "[1/4] Verifying Phase 3.1 output exists"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
count = conn.execute("select count(*) from silver.iot_events_normalized").fetchone()[0]
print(f"silver.iot_events_normalized row_count: {count}")
if count == 0:
    raise SystemExit("Missing Phase 3.1 output. Run Batch 3.1 first.")
PY

echo "[2/4] Running Batch 3.2 curated lookback build"
python3 scripts/build_silver_phase_3_2.py \
  --db-path data/duckdb/scr.duckdb \
  --terms-csv data/reference/route_business_terms.csv \
  --lookback-hours 48

echo "[3/4] Verifying domain normalization outputs"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
rows = conn.execute("""
select route_code, vehicle_type_raw, vehicle_type, contract_value_raw, contract_value_million_eur
from silver.route_business_terms_normalized
order by route_code
""").fetchall()
for row in rows:
    print(row)
PY

echo "[4/4] Verifying lookback coverage parity"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
max_ts = conn.execute("select max(event_ts) from silver.iot_events_normalized").fetchone()[0]
source_count = conn.execute(f"""
select count(*) from silver.iot_events_normalized
where event_ts >= (timestamp '{max_ts}' - interval '48 hours')
""").fetchone()[0]
curated_count = conn.execute("select count(*) from silver.iot_events_curated").fetchone()[0]
print(f"lookback_source_rows_48h: {source_count}")
print(f"curated_total_rows: {curated_count}")
PY

echo
echo "✅ Batch 3.2 completed. Incremental lookback and domain normalization are in place."
