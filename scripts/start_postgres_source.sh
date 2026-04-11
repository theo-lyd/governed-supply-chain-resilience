#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="scr_source_postgres"
POSTGRES_IMAGE="postgres:16"
POSTGRES_DB="supply_chain_source"
POSTGRES_USER="source_user"
POSTGRES_PASSWORD="source_pass"
POSTGRES_PORT="5433"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker is not installed or not on PATH."
  exit 1
fi

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Container ${CONTAINER_NAME} already exists. Starting it..."
  docker start "${CONTAINER_NAME}" >/dev/null
else
  echo "Creating and starting ${CONTAINER_NAME} on port ${POSTGRES_PORT}..."
  docker run -d \
    --name "${CONTAINER_NAME}" \
    -e POSTGRES_DB="${POSTGRES_DB}" \
    -e POSTGRES_USER="${POSTGRES_USER}" \
    -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    -p "${POSTGRES_PORT}:5432" \
    -v "${ROOT_DIR}/sql/postgres/init_source.sql:/docker-entrypoint-initdb.d/init_source.sql:ro" \
    "${POSTGRES_IMAGE}" >/dev/null
fi

echo "Postgres source simulation is running."
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: ${POSTGRES_PORT}"
echo "  DB:   ${POSTGRES_DB}"
echo "  User: ${POSTGRES_USER}"
