#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-/usr/local/bin/python}"
AIRFLOW_VENV_DIR="${AIRFLOW_VENV_DIR:-.venv-airflow}"
AIRFLOW_VERSION="${AIRFLOW_VERSION:-2.10.5}"

echo "[Airflow Setup] Creating dedicated Airflow environment"
echo "  Python: $PYTHON_BIN"
echo "  Venv:   $AIRFLOW_VENV_DIR"
echo "  Airflow:${AIRFLOW_VERSION}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "ERROR: Python binary not found: $PYTHON_BIN" >&2
  exit 1
fi

if [[ ! -d "$AIRFLOW_VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$AIRFLOW_VENV_DIR"
fi

# shellcheck disable=SC1091
source "$AIRFLOW_VENV_DIR/bin/activate"

python -m pip install --upgrade pip setuptools wheel

PY_VER="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
CONSTRAINTS_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PY_VER}.txt"

python -m pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "$CONSTRAINTS_URL"

echo ""
echo "Airflow environment is ready."
echo "Activate with: source ${AIRFLOW_VENV_DIR}/bin/activate"
echo "Check with: airflow version"
