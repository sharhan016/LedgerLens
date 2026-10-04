#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${PWD}/.cache/uv"
(cd backend && uv run --offline ruff check app tests migrations)
(cd backend && uv run --offline pytest)
(cd backend && uv run --offline alembic upgrade head --sql > /tmp/ledgerlens-routed.sql)
grep -q "CREATE TABLE product_metrics" /tmp/ledgerlens-routed.sql
npm --prefix frontend run build

