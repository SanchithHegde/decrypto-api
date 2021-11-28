#! /usr/bin/env bash

set -euxo pipefail

export PYTHONPATH="."
export SQLALCHEMY_WARN_20=true  # SQLAlchemy 2.0
export PYTHONWARNINGS=error::DeprecationWarning  # SQLAlchemy 2.0

if [ $(uname -s) = "Linux" ]; then
  echo "Removing __pycache__ files"
  find . -type d -name __pycache__ -exec rm -r {} \+
fi

python app/tests_pre_start.py

pytest --cov=app --cov-config=pyproject.toml --cov-report=term-missing app/tests "${@}"

# If HTML coverage reports are required, comment above line and uncomment below line
# pytest --cov=app --cov-config=pyproject.toml --cov-report=term-missing --cov-report=html app/tests "${@}"

