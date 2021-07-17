#! /usr/bin/env sh

set -euo pipefail

export PYTHONPATH=.

# Let the database start
python app/backend_pre_start.py

# Run alembic migrations
alembic upgrade head

# Create initial data in database
python app/initial_data.py