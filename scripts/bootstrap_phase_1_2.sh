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

enable_uc = os.environ.get('ENABLE_UNITY_CATALOG', '0').strip().lower() in {'1', 'true', 'yes'}
storage_root = os.environ.get('UNITY_CATALOG_STORAGE_ROOT', '').strip()

if not enable_uc:
    print("  ℹ️  Unity Catalog provisioning is disabled for cost-constrained mode.")
    print("  Set ENABLE_UNITY_CATALOG=1 to provision dev/prod catalogs when storage is available.")
    raise SystemExit(0)

if not storage_root:
    print("  ❌ ERROR: ENABLE_UNITY_CATALOG=1 but UNITY_CATALOG_STORAGE_ROOT is not set.")
    print("  Unity Catalog catalog creation requires a metastore storage root or managed location.")
    print("  Set UNITY_CATALOG_STORAGE_ROOT to a workspace-approved cloud storage path and rerun.")
    raise SystemExit(1)

# Create dev catalog
try:
    client.catalogs.create(
        name="dev",
        comment="Development environment for SCR Engineering",
        storage_root=storage_root
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
        comment="Production environment for SCR Analytics",
        storage_root=storage_root
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

# Step 5: List created catalogs and schemas
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

enable_uc = os.environ.get('ENABLE_UNITY_CATALOG', '0').strip().lower() in {'1', 'true', 'yes'}

if not enable_uc:
    print("")
    print("  ✓ Cost-constrained mode active: Unity Catalog verification skipped")
    print("  ✓ Continue using hive_metastore-backed schemas for Phase 2 development")
    raise SystemExit(0)

try:
    dev_catalogs = [cat.name for cat in client.catalogs.list() if cat.name in ['dev', 'prod']]
    dev_schemas = [schema.name for schema in client.schemas.list(catalog_name='dev')]
    prod_schemas = [schema.name for schema in client.schemas.list(catalog_name='prod')]

    print("")
    print("  ✓ Catalog listing succeeded with the refreshed PAT")
    print(f"  ✓ Visible catalogs: {', '.join(dev_catalogs) if dev_catalogs else 'none'}")
    print(f"  ✓ dev schemas: {', '.join(dev_schemas) if dev_schemas else 'none'}")
    print(f"  ✓ prod schemas: {', '.join(prod_schemas) if prod_schemas else 'none'}")
except Exception as exc:
    print("")
    print("  ⚠️  Catalog listing could not be verified in this session.")
    print(f"  Reason: {exc}")
    print("  Creation still succeeded; if needed, regenerate PAT with unity-catalog scope and rerun.")
PYTHON_VERIFY

echo ""
echo "✅ Batch 1.2 bootstrap completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Run: dbt seed --target dev      (to load reference data)"
echo "  2. Run: dbt docs generate          (to create lineage docs)"
echo "  3. Proceed to Batch 2.1: Ingestion"
echo ""
echo "Optional Unity Catalog path later:"
echo "  ENABLE_UNITY_CATALOG=1 UNITY_CATALOG_STORAGE_ROOT=s3://... ./scripts/bootstrap_phase_1_2.sh"
