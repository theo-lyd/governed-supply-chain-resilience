#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 2.1: Multi-Source Ingestion (Cost-Constrained Track) ==="
echo ""

echo "[1/5] Verifying Databricks environment variables"
./scripts/check_databricks_env.sh

echo "[2/5] Starting local Postgres source simulation"
./scripts/start_postgres_source.sh

echo "[3/5] Emitting IoT heartbeat files"
python3 ./scripts/iot_emitter.py --output-dir data/iot_landing --iterations 2 --interval-seconds 1 --events-per-file 15

echo "[4/5] Verifying emitted files"
ls -1 data/iot_landing | tail -n 5

echo "[5/5] Loading IoT files into Databricks Bronze table"
python3 ./scripts/ingest_iot_to_bronze.py --input-pattern "data/iot_landing/*.jsonl"

echo ""
echo "✅ Batch 2.1 local scaffolding and Bronze ingestion completed."
echo "Next: capture source-to-Bronze reconciliation evidence in the phase report."
