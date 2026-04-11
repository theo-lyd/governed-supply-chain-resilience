#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 3.1: Silver German Normalization and AGS Harmonization ==="
echo

echo "[1/4] Checking Bronze baseline"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
count = conn.execute("select count(*) from bronze.iot_events_raw").fetchone()[0]
print(f"bronze.iot_events_raw row_count: {count}")
if count == 0:
    raise SystemExit("Bronze table is empty. Run Batch 2.1/2.2 first.")
PY

echo "[2/4] Running Phase 3.1 Silver build"
python3 scripts/build_silver_phase_3_1.py --db-path data/duckdb/scr.duckdb --mapping-csv data/reference/route_ags_mapping.csv

echo "[3/4] Verifying canonical city normalization"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
rows = conn.execute("""
select route_code, origin_city, destination_city, origin_ags, destination_ags
from silver.dim_route_geo
order by route_code
""").fetchall()
for row in rows:
    print(row)
PY

echo "[4/4] Verifying Silver row counts"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
silver_count = conn.execute("select count(*) from silver.iot_events_normalized").fetchone()[0]
bronze_count = conn.execute("select count(*) from bronze.iot_events_raw").fetchone()[0]
print(f"silver.iot_events_normalized row_count: {silver_count}")
print(f"bronze.iot_events_raw row_count: {bronze_count}")
PY

echo
echo "✅ Batch 3.1 completed. Silver normalization artifacts are ready."
