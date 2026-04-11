#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/4] Checking required Databricks environment variables"
./scripts/check_databricks_env.sh

echo "[2/4] Preparing local dbt profile"
mkdir -p "$HOME/.dbt"
cp dbt/profiles.yml.example "$HOME/.dbt/profiles.yml"

echo "[3/4] Installing dbt-databricks adapter"
python3 -m pip install --upgrade pip
python3 -m pip install dbt-databricks

echo "[4/4] Running dbt debug"
dbt debug --profile governed_supply_chain_resilience --target dev

echo "Batch 1.1 bootstrap completed successfully."