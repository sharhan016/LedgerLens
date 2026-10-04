.PHONY: install dev-api dev-web demo demo-down test-backend test-web build-web verify verify-foundation

install:
	cd backend && UV_CACHE_DIR=../.cache/uv uv sync --all-groups --extra ml
	cd frontend && npm ci

dev-api:
	cd backend && UV_CACHE_DIR=../.cache/uv uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	cd frontend && npm run dev

demo:
	docker compose up --build

demo-down:
	docker compose down

test-backend:
	cd backend && UV_CACHE_DIR=../.cache/uv uv run pytest

test-web:
	cd frontend && npm test

build-web:
	cd frontend && npm run build

verify-foundation:
	bash scripts/verify/01-foundation.sh

verify:
	bash scripts/verify/09-integrated-demo.sh
