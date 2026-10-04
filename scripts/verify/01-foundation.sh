#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${PWD}/.cache/uv"

python3 scripts/validate_foundation.py
(cd backend && uv run --offline ruff check app tests)
(cd backend && uv run --offline pytest)
npm --prefix frontend run build
python3 /Users/sharhan/.agents/skills/webapp-testing/scripts/with_server.py \
  --server "cd backend && UV_CACHE_DIR=../.cache/uv uv run --offline uvicorn app.main:app --host 127.0.0.1 --port 8000" --port 8000 \
  --server "npm --prefix frontend run dev -- --host 127.0.0.1" --port 5173 \
  -- python3 scripts/playwright/foundation_smoke.py
