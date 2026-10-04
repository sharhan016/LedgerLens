#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${PWD}/.cache/uv"
(cd backend && uv run --offline ruff check app tests migrations scripts)
(cd backend && uv run --offline pytest \
  tests/test_security.py \
  tests/test_tenant_documents.py \
  tests/test_authorized_api.py \
  tests/test_migration_contract.py)
(cd backend && uv run --offline alembic upgrade head --sql > /tmp/ledgerlens-migration.sql)
grep -q "CREATE EXTENSION IF NOT EXISTS vector" /tmp/ledgerlens-migration.sql
grep -q "CREATE TABLE audit_events" /tmp/ledgerlens-migration.sql

