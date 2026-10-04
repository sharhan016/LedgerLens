#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${PWD}/.cache/uv"
(cd backend && uv run --offline ruff check app tests migrations)
(cd backend && uv run --offline pytest)
(cd backend && uv run --offline alembic upgrade head --sql > /tmp/ledgerlens-operations.sql)
grep -q "CREATE TABLE conversations" /tmp/ledgerlens-operations.sql
grep -q "CREATE TABLE semantic_cache_entries" /tmp/ledgerlens-operations.sql
(cd backend && uv run --offline python -m app.evaluation.benchmark \
  --dataset ../evaluation/datasets/banking-rag-v1.jsonl \
  --corpus ../data/sample/banking \
  --output /tmp/ledgerlens-evaluation-report.json)
npm --prefix frontend run build

