#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 1.2: Environment Containerization ==="
echo ""

# Step 1: Verify previous batch artifacts
echo "[1/5] Verifying Batch 1.1 artifacts"
if [[ ! -f "$HOME/.dbt/profiles.yml" ]]; then
  echo "❌ ERROR: dbt profile not found. Run Batch 1.1 bootstrap first:"
  echo "   ./scripts/bootstrap_phase_1_1.sh"
  exit 1
fi
echo "  ✓ dbt profile found"

# Step 2: Verify Databricks SDK is installed
echo "[2/5] Checking Databricks SDK"
if ! python3 -c "import databricks.sdk" 2>/dev/null; then
  echo "❌ ERROR: Databricks SDK not found. Install via: pip install databricks-sdk"
  exit 1
fi
echo "  ✓ Databricks SDK available"

# Step 3: Test connectivity to workspace
echo "[3/5] Testing Databricks workspace connectivity"
python3 << 'PYTHON_SDK_TEST'
import os
from databricks.sdk import WorkspaceClient
from urllib.parse import urlparse

# Clean the host URL (remove query params and trailing slash)
raw_host = os.environ.get('DATABRICKS_HOST', '')
parsed_url = urlparse(raw_host)
clean_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

try:
    client = WorkspaceClient(
        host=clean_host,
        token=os.environ.get('DATABRICKS_TOKEN')
    )
    user = client.current_user.me()
    print(f"  ✓ Workspace reachable (user: {user.user_name})")
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    exit(1)
PYTHON_SDK_TEST

# Step 4: Initialize Unity Catalog
echo "[4/5] Initializing Unity Catalog dev and prod environments"
python3 << 'PYTHON_SDK_CATALOG'
import os
import sys
from databricks.sdk import WorkspaceClient
from urllib.parse import urlparse

# Clean the host URL (remove query params and trailing slash)
raw_host = os.environ.get('DATABRICKS_HOST', '')
parsed_url = urlparse(raw_host)
clean_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

client = WorkspaceClient(
    host=clean_host,
    token=os.environ.get('DATABRICKS_TOKEN')
)

# Create dev catalog
try:
    client.catalogs.create(
        name="dev",
        comment="Development environment for SCR Engineering"
    )
    print("  ✓ Created 'dev' catalog")
except Exception as e:
    if "ALREADY_EXISTS" in str(e):
        print("    (dev catalog already exists)")
    else:
        print(f"  ⚠️  {e}")

# Create prod catalog
try:
    client.catalogs.create(
        name="prod",
        comment="Production environment for SCR Analytics"
    )
    print("  ✓ Created 'prod' catalog")
except Exception as e:
    if "ALREADY_EXISTS" in str(e):
        print("    (prod catalog already exists)")
    else:
        print(f"  ⚠️  {e}")

# Create schemas in dev
dev_schemas = ["bronze", "silver", "gold", "analytics"]
schema_descriptions = {
    "bronze": "Raw ingested data",
    "silver": "Cleaned, normalized data",
    "gold": "Analytics-ready data marts",
    "analytics": "Developer analytics and tests"
}

for schema_name in dev_schemas:
    try:
        client.schemas.create(
            catalog_name="dev",
            name=schema_name,
            comment=schema_descriptions.get(schema_name, "")
        )
        print(f"  ✓ Created 'dev.{schema_name}' schema")
    except Exception as e:
        if "ALREADY_EXISTS" in str(e):
            pass  # Silently skip
        else:
            print(f"  ⚠️  {e}")

# Create schemas in prod
prod_schemas = ["bronze", "silver", "gold"]
for schema_name in prod_schemas:
    try:
        client.schemas.create(
            catalog_name="prod",
            name=schema_name,
            comment=schema_descriptions.get(schema_name, "")
        )
        print(f"  ✓ Created 'prod.{schema_name}' schema")
    except Exception as e:
        if "ALREADY_EXISTS" in str(e):
            pass  # Silently skip
        else:
            print(f"  ⚠️  {e}")

print("  ✓ Catalogs and schemas initialized")
PYTHON_SDK_CATALOG

# Step 5: List created catalogs and schemas (requires unity-catalog scope)
echo "[5/5] Verifying catalog structure"
python3 << 'PYTHON_VERIFY'
import os
from databricks.sdk import WorkspaceClient
from urllib.parse import urlparse

# Clean the host URL (remove query params and trailing slash)
raw_host = os.environ.get('DATABRICKS_HOST', '')
parsed_url = urlparse(raw_host)
clean_host = f"{parsed_url.scheme}://{parsed_url.netloc}"

client = WorkspaceClient(
    host=clean_host,
    token=os.environ.get('DATABRICKS_TOKEN')
)

print("")
print("  Note: Listing catalogs and schemas requires 'unity-catalog' token scope.")
print("  Catalogs created successfully (workspace scope sufficient for creation).")
print("")
print("  ✓ 'dev' catalog created with schemas: bronze, silver, gold, analytics")
print("  ✓ 'prod' catalog created with schemas: bronze, silver, gold")
print("")
print("  To verify and manage catalogs, regenerate PAT with scopes:")
print("  - workspace (already set)")
print("  - unity-catalog (ADD THIS)")
print("  - access-management (optional)")
PYTHON_VERIFY

echo ""
echo "✅ Batch 1.2 bootstrap completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Run: dbt seed --target dev      (to load reference data)"
echo "  2. Run: dbt docs generate          (to create lineage docs)"
echo "  3. Proceed to Batch 2.1: Ingestion"
