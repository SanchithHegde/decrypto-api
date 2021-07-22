#! /usr/bin/env sh

set -euxo pipefail

export PYTHONPATH=.

if [ $(uname -s) = "Linux" ]; then
  echo "Removing __pycache__ files"
  find . -type d -name __pycache__ -exec rm -r {} \+
fi

python app/tests_pre_start.py

pytest --cov=app --cov-report=term-missing app/tests "${@}"

# If HTML coverage reports are required, comment above line and uncomment below line
# pytest --cov=app --cov-report=term-missing --cov-report=html app/tests "${@}"

