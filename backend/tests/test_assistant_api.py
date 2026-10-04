import uuid

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.generation.providers import DeterministicGroundedProvider
from app.generation.service import AssistantService
from app.generation.service_dependencies import get_assistant_service
from app.main import app
from app.retrieval.domain import RetrievalCandidate
from app.security.principal import Principal, Role
from app.security.tokens import TokenService


class StubRetrieval:
    def __init__(self, candidate: RetrievalCandidate) -> None:
        self.candidate = candidate

    async def search(self, principal, query, *, route="hybrid_knowledge"):  # type: ignore[no-untyped-def]
        assert principal.tenant_id == self.candidate.tenant_id
        return [self.candidate]


def test_assistant_api_exposes_citations_passages_grounding_trace_and_latency() -> None:
    tenant_id = uuid.uuid4()
    principal = Principal(uuid.uuid4(), tenant_id, Role.ANALYST)
    candidate = RetrievalCandidate(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        tenant_id=tenant_id,
        title="KYC Manual",
        source="kyc-aml-manual.md",
        version="2026.3",
        content="KYC requires a government-issued photo identity document.",
        section="Standard KYC evidence",
        page_number=4,
        allowed_roles=("analyst",),
        dense_score=0.91,
        keyword_score=0.82,
        rrf_score=0.032,
        rerank_score=0.97,
    )
    service = AssistantService(
        retrieval=StubRetrieval(candidate),  # type: ignore[arg-type]
        provider=DeterministicGroundedProvider(
            "KYC requires a government-issued photo identity document [S1]."
        ),
    )
    app.dependency_overrides[get_assistant_service] = lambda: service
    token = TokenService(get_settings()).issue(principal)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/assistant/ask",
                headers={"Authorization": f"Bearer {token}"},
                json={"question": "What identity document does KYC require?"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["citations"][0]["source"] == "kyc-aml-manual.md"
    assert body["citations"][0]["page_number"] == 4
    assert body["passages"][0]["rerank_score"] == 0.97
    assert body["grounding"]["grounded"] is True
    assert body["query_trace"]["route"] == "hybrid_knowledge"
    assert set(body["latency_ms"]) == {
        "planning",
        "retrieval",
        "generation",
        "validation",
        "operations",
        "total",
    }
    assert body["conversation_id"] is None
    assert body["cache_hit"] is False
