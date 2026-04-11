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
  echo "\nOne or more required Databricks environment variables are missing."
  echo "Set them in GitHub Codespaces Secrets, then restart the terminal/session."
  exit 1
fi

echo "\nAll required Databricks environment variables are present."
