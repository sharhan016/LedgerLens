import uuid

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.retrieval.dependencies import get_retrieval_orchestrator
from app.retrieval.domain import RetrievalCandidate
from app.security.principal import Principal, Role
from app.security.tokens import TokenService


class StubOrchestrator:
    def __init__(self, passage: RetrievalCandidate) -> None:
        self.passage = passage

    async def search(self, principal, query):  # type: ignore[no-untyped-def]
        assert principal.tenant_id == self.passage.tenant_id
        assert query == "minimum premium balance"
        return [self.passage]


def test_retrieval_api_exposes_passage_and_component_scores() -> None:
    tenant_id = uuid.uuid4()
    principal = Principal(uuid.uuid4(), tenant_id, Role.ANALYST)
    passage = RetrievalCandidate(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        tenant_id=tenant_id,
        title="Premium Savings Policy",
        source="premium-savings-policy.md",
        version="2026.2",
        content="The average monthly balance is INR 25,000.",
        section="Balance requirement",
        page_number=None,
        allowed_roles=("analyst",),
        dense_score=0.88,
        keyword_score=0.74,
        rrf_score=0.032,
        rerank_score=0.96,
    )
    app.dependency_overrides[get_retrieval_orchestrator] = lambda: StubOrchestrator(passage)
    token = TokenService(get_settings()).issue(principal)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/retrieval/search",
                headers={"Authorization": f"Bearer {token}"},
                json={"query": "minimum premium balance"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    result = response.json()["passages"][0]
    assert result["source"] == "premium-savings-policy.md"
    assert result["section"] == "Balance requirement"
    assert result["dense_score"] == 0.88
    assert result["keyword_score"] == 0.74
    assert result["rrf_score"] == 0.032
    assert result["rerank_score"] == 0.96

