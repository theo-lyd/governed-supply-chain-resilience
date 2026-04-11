#!/usr/bin/env bash
set -euo pipefail

required_vars=(
  DATABRICKS_HOST
  DATABRICKS_HTTP_PATH
  DATABRICKS_TOKEN
)

missing=0
for v in "${required_vars[@]}"; do
  if [[ -z "${!v:-}" ]]; then
    echo "MISSING: $v"
    missing=1
  else
    echo "OK: $v is set"
  fi
done

if [[ "$missing" -eq 1 ]]; then
  echo "\nDatabricks extension-path variables are not fully configured."
  echo "This is optional for the DuckDB-first track; configure only if running Databricks extension workflows."
  exit 1
fi

echo "\nAll required Databricks environment variables are present."
