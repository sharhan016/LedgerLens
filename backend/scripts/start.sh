#!/bin/sh
set -eu

alembic upgrade head
if [ "${LEDGERLENS_DEMO_SEED_ENABLED:-false}" = "true" ]; then
  python -m app.bootstrap.demo
fi
exec uvicorn app.main:app --host "${LEDGERLENS_API_HOST:-0.0.0.0}" --port "${LEDGERLENS_API_PORT:-8000}"
