#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${PWD}/.cache/uv"
(cd backend && uv run --offline ruff check app tests migrations)
(cd backend && uv run --offline pytest)
(cd backend && uv run --offline alembic upgrade head --sql > /tmp/ledgerlens-release.sql)
grep -q "CREATE TABLE conversations" /tmp/ledgerlens-release.sql
(cd backend && uv run --offline python -m app.evaluation.benchmark \
  --dataset ../evaluation/datasets/banking-rag-v1.jsonl \
  --corpus ../data/sample/banking \
  --output /tmp/ledgerlens-evaluation-report.json)
npm --prefix frontend test
npm --prefix frontend run build
python3 scripts/validate_release.py
python3 /Users/sharhan/.agents/skills/webapp-testing/scripts/with_server.py \
  --server "npm --prefix frontend run dev -- --host 127.0.0.1" --port 5173 \
  -- node scripts/playwright/workspace_smoke.mjs
