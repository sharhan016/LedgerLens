import uuid

from fastapi.testclient import TestClient

from app.api.documents import get_document_service
from app.core.config import get_settings
from app.main import app
from app.repositories.documents import DocumentRecord, InMemoryDocumentRepository
from app.security.principal import Principal, Role
from app.security.tokens import TokenService
from app.services.documents import DocumentService


def test_document_api_returns_404_for_a_cross_tenant_identifier() -> None:
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    foreign = DocumentRecord(
        id=uuid.uuid4(),
        tenant_id=tenant_b,
        title="Foreign tenant policy",
        source_type="policy",
        version="1",
        status="ready",
        allowed_roles=(Role.ANALYST.value,),
    )
    service = DocumentService(InMemoryDocumentRepository([foreign]))
    app.dependency_overrides[get_document_service] = lambda: service
    principal = Principal(uuid.uuid4(), tenant_a, Role.ANALYST)
    token = TokenService(get_settings()).issue(principal)

    try:
        with TestClient(app) as client:
            response = client.get(
                f"/api/v1/documents/{foreign.id}",
                headers={"Authorization": f"Bearer {token}"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_document_api_requires_a_bearer_token() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/documents")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

