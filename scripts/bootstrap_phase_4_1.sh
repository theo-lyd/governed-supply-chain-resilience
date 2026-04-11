#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 4.1: Gold SCD2 and Point-in-Time Join ==="
echo

echo "[1/4] Verifying Phase 3 curated baseline"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
count = conn.execute("select count(*) from silver.iot_events_curated").fetchone()[0]
print(f"silver.iot_events_curated row_count: {count}")
if count == 0:
    raise SystemExit("Missing Phase 3 curated data. Run Batch 3.2 first.")
PY

echo "[2/4] Running Phase 4.1 gold build"
python3 scripts/build_gold_phase_4_1.py \
  --db-path data/duckdb/scr.duckdb \
  --supplier-history-csv data/reference/supplier_reliability_history.csv \
  --route-supplier-csv data/reference/route_supplier_mapping.csv

echo "[3/4] Verifying SCD2 current rows"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
rows = conn.execute("""
select supplier_id, reliability_score, valid_from, valid_to, is_current
from gold.dim_supplier_reliability_scd2
order by supplier_id, valid_from
""").fetchall()
for row in rows:
    print(row)
PY

echo "[4/4] Verifying point-in-time join coverage"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
silver_count = conn.execute("select count(*) from silver.iot_events_curated").fetchone()[0]
gold_count = conn.execute("select count(*) from gold.fact_iot_events_pit").fetchone()[0]
null_suppliers = conn.execute("select count(*) from gold.fact_iot_events_pit where supplier_id is null").fetchone()[0]
print(f"silver_rows: {silver_count}")
print(f"gold_rows: {gold_count}")
print(f"gold_rows_with_null_supplier: {null_suppliers}")
PY

echo
echo "✅ Batch 4.1 completed. Gold SCD2 and PIT artifacts are ready."
