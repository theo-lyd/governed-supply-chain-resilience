#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Batch 1.2: Environment Containerization (DuckDB-Native) ==="
echo

echo "[1/5] Verifying Batch 1.1 artifacts"
if [[ ! -f "$HOME/.dbt/profiles.yml" ]]; then
  echo "ERROR: dbt profile not found. Run ./scripts/bootstrap_phase_1_1.sh first"
  exit 1
fi
echo "  OK: dbt profile found"

echo "[2/5] Checking local tooling"
./scripts/check_duckdb_env.sh

echo "[3/5] Verifying Python packages"
python3 - <<'PY'
import importlib
mods = ["duckdb", "dbt"]
missing = [m for m in mods if importlib.util.find_spec(m) is None]
if missing:
    raise SystemExit(f"Missing modules: {', '.join(missing)}")
print("  OK: duckdb and dbt are installed")
PY

echo "[4/5] Initializing local medallion schemas"
python3 - <<'PY'
import os
from pathlib import Path
import duckdb

path = os.environ.get("DUCKDB_PATH", "data/duckdb/scr.duckdb")
Path(path).parent.mkdir(parents=True, exist_ok=True)
conn = duckdb.connect(path)
for schema in ["bronze", "silver", "gold", "analytics"]:
    conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
print("  OK: schemas initialized in", path)
PY

echo "[5/5] Verifying schema structure"
python3 - <<'PY'
import os
import duckdb
path = os.environ.get("DUCKDB_PATH", "data/duckdb/scr.duckdb")
conn = duckdb.connect(path)
rows = conn.execute("select schema_name from information_schema.schemata where schema_name in ('bronze','silver','gold','analytics') order by schema_name").fetchall()
print("  OK: schemas:", ", ".join(r[0] for r in rows))
PY

echo
echo "Batch 1.2 bootstrap completed successfully."
echo "Next: proceed to Batch 2.1 using local DuckDB Bronze ingestion."
