import uuid

from fastapi.testclient import TestClient

from app.api.ingestion import get_ingestion_pipeline
from app.core.config import get_settings
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.repository import InMemoryIngestionRepository
from app.main import app
from app.security.principal import Principal, Role
from app.security.tokens import TokenService


def token(role: Role, tenant_id: uuid.UUID | None = None) -> str:
    principal = Principal(uuid.uuid4(), tenant_id or uuid.uuid4(), role)
    return TokenService(get_settings()).issue(principal)


def test_compliance_user_can_ingest_markdown_and_receive_real_status() -> None:
    repository = InMemoryIngestionRepository()
    pipeline = IngestionPipeline(repository)
    app.dependency_overrides[get_ingestion_pipeline] = lambda: pipeline

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/ingestion/documents",
                headers={"Authorization": f"Bearer {token(Role.COMPLIANCE)}"},
                files={"file": ("policy.md", b"# Rules\nSynthetic policy text.", "text/markdown")},
                data={"title": "Policy", "version": "1", "source_type": "policy"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["status"] == "ready"
    assert response.json()["chunks"][0]["section"] == "Rules"
    assert len(repository.documents) == 1


def test_viewer_cannot_ingest_documents() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/ingestion/documents",
            headers={"Authorization": f"Bearer {token(Role.VIEWER)}"},
            files={"file": ("policy.md", b"# Rules\nSynthetic policy text.", "text/markdown")},
            data={"title": "Policy", "version": "1"},
        )

    assert response.status_code == 403
    assert response.json() == {"detail": "Permission denied"}

