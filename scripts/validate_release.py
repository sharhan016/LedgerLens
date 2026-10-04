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
    "VITE_API_BASE_URL: http://localhost:8000",
)
require("backend/Dockerfile", "alembic.ini", "migrations", "scripts/start.sh", "INSTALL_ML")
require("backend/scripts/start.sh", "alembic upgrade head", "app.bootstrap.demo")
require("frontend/Dockerfile", "npm run build", "nginx:1.27-alpine")
require("README.md", "demo-extractive-not-llm", "deterministic_demo")
print("release contracts validated")
