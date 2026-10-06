from pathlib import Path


def require(path: str, *fragments: str) -> None:
    content = Path(path).read_text(encoding="utf-8")
    missing = [fragment for fragment in fragments if fragment not in content]
    if missing:
        raise SystemExit(f"{path} is missing release contract: {missing}")


require(
    "docker-compose.yml",
    "pgvector/pgvector:pg16",
    "condition: service_healthy",
    'LEDGERLENS_DEMO_SEED_ENABLED: "true"',
    "VITE_API_BASE_URL: ${VITE_API_BASE_URL:-http://localhost:8000}",
)
require("backend/Dockerfile", "alembic.ini", "migrations", "scripts/start.sh", "INSTALL_ML")
require("backend/scripts/start.sh", "alembic upgrade head", "app.bootstrap.demo")
require("frontend/Dockerfile", "npm run build", "nginx:1.27-alpine")
require("frontend/nginx.conf", "proxy_pass http://backend:8000", "try_files")
require(
    "docker-compose.production.yml",
    "ledgerlens_postgres",
    "traefik.http.routers.ledgerlens.rule=Host(`ledgerlens.sharhan.dev`)",
    "traefik.http.services.ledgerlens.loadbalancer.server.port=80",
    "LEDGERLENS_API_DOCS_ENABLED",
)
require(
    ".github/workflows/deploy-hostinger.yml",
    "astral-sh/setup-uv@v10.2.0",
    "hostinger/deploy-on-vps@v2",
    "docker-compose.production.yml",
    "api-key: ${{ secrets.HOSTINGER_API_KEY }}",
    "virtual-machine: ${{ secrets.HOSTINGER_VM_ID }}",
)
require(
    "docs/deployment/hostinger.md",
    "`network_mode: host`",
    "No shared Docker network is required",
    "host-to-LedgerLens-bridge",
)
require("README.md", "demo-extractive-not-llm", "deterministic_demo")
print("release contracts validated")
