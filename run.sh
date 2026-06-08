#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f backend/.env ]; then
  # Normalize Windows-edited env files before sourcing.
  sed -i 's/\r$//' backend/.env
  set -o allexport
  source backend/.env
  set +o allexport
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
RELOAD_FLAG=""

if [ "${UVICORN_RELOAD:-true}" = "true" ]; then
  RELOAD_FLAG="--reload"
fi

echo "Starting 一命千途 on ${HOST}:${PORT}"
python -m uvicorn backend.app.main:app --host "$HOST" --port "$PORT" ${RELOAD_FLAG}
