#!/usr/bin/env bash
set -euo pipefail

missing=0
for cmd in python3 pip; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "MISSING: $cmd"
    missing=1
  else
    echo "OK: $cmd is available"
  fi
done

if [[ "$missing" -eq 1 ]]; then
  echo
  echo "One or more required local tools are missing."
  echo "Install Python and pip in this Codespace, then rerun."
  exit 1
fi

echo
if [[ -n "${DUCKDB_PATH:-}" ]]; then
  echo "DUCKDB_PATH is set to: ${DUCKDB_PATH}"
else
  echo "DUCKDB_PATH is not set; default will be used: data/duckdb/scr.duckdb"
fi

echo "Local DuckDB environment checks passed."
