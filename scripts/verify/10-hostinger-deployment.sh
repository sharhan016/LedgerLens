#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${PWD}/.cache/uv"

(cd backend && uv run --offline ruff check app tests migrations)
(cd backend && uv run --offline pytest tests/test_config.py tests/test_system_api.py)
npm --prefix frontend test
VITE_API_BASE_URL="" npm --prefix frontend run build
if rg -n "localhost|127\.0\.0\.1" frontend/dist; then
  echo "production frontend artifact contains a loopback address" >&2
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  compose=(docker compose)
elif docker-compose version >/dev/null 2>&1; then
  compose=(docker-compose)
else
  echo "Docker Compose is required to validate the Hostinger contract" >&2
  exit 1
fi

compose_output="/tmp/ledgerlens-production-compose.json"
LEDGERLENS_ENV=showcase \
POSTGRES_PASSWORD=validation-password \
LEDGERLENS_JWT_SECRET=validation-secret-with-at-least-thirty-two-characters \
  "${compose[@]}" -f docker-compose.production.yml config --format json > "${compose_output}"

python3 - "${compose_output}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as source:
    compose = json.load(source)

services = compose["services"]
assert set(services) == {"backend", "db", "frontend"}
assert all(not service.get("ports") for service in services.values())
assert services["frontend"]["build"]["args"]["VITE_API_BASE_URL"] == ""
assert services["frontend"]["labels"]["traefik.http.routers.ledgerlens.rule"] == (
    "Host(`ledgerlens.sharhan.dev`)"
)
assert services["frontend"]["labels"][
    "traefik.http.services.ledgerlens.loadbalancer.server.port"
] == "80"
assert compose["networks"]["traefik"]["external"] is True
assert any(
    volume["target"] == "/var/lib/postgresql/data"
    for volume in services["db"]["volumes"]
)
PY

python3 scripts/validate_release.py
echo "Hostinger deployment contracts validated"
