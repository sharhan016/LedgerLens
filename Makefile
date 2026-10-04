.PHONY: install dev-api dev-web test-backend build-web verify-foundation

install:
	cd backend && UV_CACHE_DIR=../.cache/uv uv sync --all-groups --extra ml
	cd frontend && npm ci

dev-api:
	cd backend && UV_CACHE_DIR=../.cache/uv uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd frontend && npm run dev

test-backend:
	cd backend && UV_CACHE_DIR=../.cache/uv uv run pytest

build-web:
	cd frontend && npm run build

verify-foundation:
	bash scripts/verify/01-foundation.sh
