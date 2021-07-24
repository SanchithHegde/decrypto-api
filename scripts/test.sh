#! /usr/bin/env sh

set -euxo pipefail

export PYTHONPATH="."
export POSTGRES_DB="decrypto_test"

# Run prestart.sh script in the "scripts" directory before starting
PRE_START_PATH="scripts/prestart.sh"
echo "Running pre-start script ${PRE_START_PATH}"
sh "${PRE_START_PATH}"

if [ $(uname -s) = "Linux" ]; then
  echo "Removing __pycache__ files"
  find . -type d -name __pycache__ -exec rm -r {} \+
fi

python app/tests_pre_start.py

pytest --cov=app --cov-report=term-missing app/tests "${@}"

# If HTML coverage reports are required, comment above line and uncomment below line
# pytest --cov=app --cov-report=term-missing --cov-report=html app/tests "${@}"

