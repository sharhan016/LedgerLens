#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${PWD}/.cache/uv"
(cd backend && uv run --offline ruff check app tests migrations)
(cd backend && uv run --offline pytest)
(cd backend && uv run --offline alembic upgrade head --sql > /tmp/ledgerlens-retrieval.sql)
grep -q "USING gin (search_vector)" /tmp/ledgerlens-retrieval.sql
grep -q "USING hnsw (embedding vector_cosine_ops)" /tmp/ledgerlens-retrieval.sql
npm --prefix frontend run build

