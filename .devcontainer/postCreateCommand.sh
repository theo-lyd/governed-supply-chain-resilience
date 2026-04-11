#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[PostCreateCommand] Starting Codespace post-create setup..."

# Update system packages
echo "[1/7] Updating system packages"
apt-get update && apt-get install -y --no-upgrade git

# Install DuckDB-first dbt core dependencies
echo "[2/7] Installing dbt-duckdb core"
python3 -m pip install --upgrade pip
python3 -m pip install dbt-duckdb

# Databricks tooling is optional in this DuckDB-first track.
echo "[3/7] Skipping Databricks CLI/dbt-databricks in base env (install on-demand if needed)"

# Airflow is intentionally kept out of the base environment.
echo "[4/7] Skipping Apache Airflow in base env (use dedicated venv script when needed)"

# Install additional development tools
echo "[5/7] Installing development tools (click, pyyaml, requests)"
python3 -m pip install click==8.3.2 pyyaml==6.0.3 requests==2.31.0

# Create marker directories
echo "[6/7] Creating workspace structure"
mkdir -p logs incidents/
chmod +x scripts/*.sh 2>/dev/null || true

# Environment check
echo "[7/7] Validating environment"
echo "  Python: $(python3 --version)"
echo "  Databricks CLI: $(databricks --version 2>/dev/null || echo 'not yet configured')"
echo "  dbt: $(dbt --version 2>/dev/null | head -1 || echo 'will be available after profile setup')"
echo ""
echo "✅ Postsetup complete!"
echo ""
echo "Next steps:"
echo "  1. Verify DuckDB profile and run dbt debug"
echo "  2. Run: ./scripts/bootstrap_phase_1_1.sh  (already done -skip if verified)"
echo "  3. Run: ./scripts/bootstrap_phase_1_2.sh  (catalogs + seeds)"
echo "  4. Optional (Phase 6): ./scripts/setup_airflow_venv.sh"
echo "  5. Optional: install Databricks tooling only for extension scenarios"
echo "  6. Verify: dbt debug && dbt docs generate"
