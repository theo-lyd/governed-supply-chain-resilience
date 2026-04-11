#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 2.1: Multi-Source Ingestion (DuckDB-Native Track) ==="
echo ""

echo "[1/5] Starting local Postgres source simulation"
./scripts/start_postgres_source.sh

echo "[2/5] Emitting IoT heartbeat files"
python3 ./scripts/iot_emitter.py --output-dir data/iot_landing --iterations 2 --interval-seconds 1 --events-per-file 15

echo "[3/5] Verifying emitted files"
ls -1 data/iot_landing | tail -n 5

echo "[4/5] Loading IoT files into DuckDB Bronze table"
python3 ./scripts/ingest_iot_to_duckdb.py --input-pattern "data/iot_landing/*.jsonl"

echo "[5/5] Quick verification query"
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
count = conn.execute("select count(*) from bronze.iot_events_raw").fetchone()[0]
print(f"bronze.iot_events_raw row_count: {count}")
PY

echo ""
echo "✅ Batch 2.1 DuckDB-native ingestion completed."
