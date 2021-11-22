#! /usr/bin/env bash

set -euo pipefail

APP_MODULE="app.main:app"
APP_DIR="app"
HOST="localhost"
PORT="8000"
LOG_LEVEL="info"

# Run prestart.sh script in the "scripts" directory before starting
PRE_START_PATH="scripts/prestart.sh"
echo "Running pre-start script ${PRE_START_PATH}"
bash "${PRE_START_PATH}"

# Start Uvicorn with live reload
exec uvicorn --reload --reload-dir "${APP_DIR}" --host "${HOST}" --port "${PORT}" --log-level "${LOG_LEVEL}" "${APP_MODULE}"