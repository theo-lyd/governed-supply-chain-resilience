#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="scr_source_postgres"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker is not installed or not on PATH."
  exit 1
fi

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker stop "${CONTAINER_NAME}" >/dev/null || true
  docker rm "${CONTAINER_NAME}" >/dev/null || true
  echo "Stopped and removed ${CONTAINER_NAME}."
else
  echo "Container ${CONTAINER_NAME} does not exist."
fi
