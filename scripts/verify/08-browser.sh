#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${PWD}/.cache/uv"
(cd backend && uv run --offline ruff check app tests migrations)
(cd backend && uv run --offline pytest)
npm --prefix frontend test
npm --prefix frontend run build
python3 /Users/sharhan/.agents/skills/webapp-testing/scripts/with_server.py \
  --server "npm --prefix frontend run dev -- --host 127.0.0.1" --port 5173 \
  -- node scripts/playwright/workspace_smoke.mjs
