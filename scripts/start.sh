#! /usr/bin/env sh

set -euo pipefail

APP_MODULE="app.main:app"
GUNICORN_CONF="gunicorn_conf.py"
WORKER_CLASS="uvicorn.workers.UvicornWorker"

# Run prestart.sh script in the "scripts" directory before starting
PRE_START_PATH="scripts/prestart.sh"
echo "Running pre-start script ${PRE_START_PATH}"
sh "${PRE_START_PATH}"

# Start Gunicorn
exec gunicorn -k "${WORKER_CLASS}" -c "${GUNICORN_CONF}" "${APP_MODULE}"
