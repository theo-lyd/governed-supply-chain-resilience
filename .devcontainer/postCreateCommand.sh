#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[PostCreateCommand] Starting Codespace post-create setup..."

# Update system packages
echo "[1/7] Updating system packages"
apt-get update && apt-get install -y --no-upgrade git

# Install Databricks CLI (pinned version)
echo "[2/7] Installing Databricks CLI (v0.234.0)"
python3 -m pip install --upgrade pip
python3 -m pip install databricks-cli==0.234.0

# Install dbt-databricks (pinned version)
echo "[3/7] Installing dbt-databricks (v1.11.6)"
python3 -m pip install dbt-databricks==1.11.6

# Install Airflow core dependencies for Phase 2 preview (pinned)
echo "[4/7] Installing Apache Airflow (v2.8.4) - Optional for Preview"
# python3 -m pip install apache-airflow==2.8.4 2>/dev/null || echo "  ⚠️  Airflow install skipped (can be done on-demand in Phase 2)"

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
echo "  1. Ensure GitHub Codespaces Secrets are set (DATABRICKS_HOST, HTTP_PATH, TOKEN)"
echo "  2. Run: ./scripts/bootstrap_phase_1_1.sh  (already done -skip if verified)"
echo "  3. Run: ./scripts/bootstrap_phase_1_2.sh  (catalogs + seeds)"
echo "  4. Verify: dbt debug && dbt docs generate"
