import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: str) -> str:
    target = ROOT / path
    assert target.is_file(), f"required file missing: {path}"
    return target.read_text(encoding="utf-8")


def main() -> None:
    package = json.loads(require("frontend/package.json"))
    backend = tomllib.loads(require("backend/pyproject.toml"))
    compose = require("docker-compose.yml")
    plan = require("docs/architecture/delivery-plan.md")
    overview = require("docs/architecture/system-overview.md")

    assert package["scripts"]["build"] == "tsc -b && vite build"
    assert "fastapi" in " ".join(backend["project"]["dependencies"]).lower()
    for service in ("db:", "backend:", "frontend:"):
        assert service in compose, f"compose service missing: {service}"
    assert "pgvector/pgvector" in compose
    assert "T-01" in plan and "T-09" in plan
    assert "Authorization before retrieval" not in overview or "authorization" in overview.lower()
    assert "Vertex" in require("README.md")
    assert (ROOT / ".vertex" / "project.json").is_file()
    print("foundation structure and architecture assertions passed")


if __name__ == "__main__":
    main()

