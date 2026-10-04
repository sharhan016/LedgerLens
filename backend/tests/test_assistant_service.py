import uuid

import pytest

from app.generation.providers import DeterministicGroundedProvider
from app.generation.service import AssistantService
from app.retrieval.domain import RetrievalCandidate
from app.security.principal import Principal, Role


class StubRetrieval:
    def __init__(self, passages: list[RetrievalCandidate]) -> None:
        self.passages = passages
        self.queries: list[str] = []

    async def search(self, principal, query):  # type: ignore[no-untyped-def]
        self.queries.append(query)
        return self.passages


def passage(tenant_id: uuid.UUID) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        tenant_id=tenant_id,
        title="Premium Savings Account Policy",
        source="premium-savings-policy.md",
        version="2026.2",
        content="The account requires an average monthly balance of INR 25,000.",
        section="Balance requirement",
        page_number=None,
        allowed_roles=("analyst",),
        dense_score=0.9,
        keyword_score=0.8,
        rrf_score=0.032,
        rerank_score=0.95,
    )


@pytest.mark.asyncio
async def test_assistant_returns_grounded_answer_and_full_inspection_trace() -> None:
    tenant_id = uuid.uuid4()
    retrieval = StubRetrieval([passage(tenant_id)])
    provider = DeterministicGroundedProvider(
        "The required average monthly balance is INR 25,000 [S1]."
    )
    service = AssistantService(retrieval=retrieval, provider=provider)  # type: ignore[arg-type]
    principal = Principal(uuid.uuid4(), tenant_id, Role.ANALYST)

    result = await service.answer(principal, "What is the minimum balance?")

    assert result.answer.endswith("[S1].")
    assert result.sources[0].source_id == "S1"
    assert result.sources[0].section == "Balance requirement"
    assert result.passages[0].rerank_score == 0.95
    assert result.grounding.grounded is True
    assert result.grounding.confidence > 0.9
    assert result.plan.route == "hybrid_knowledge"
    assert result.latency_ms["total"] >= 0
    assert provider.requests[0].context.startswith("[S1] Premium Savings Account Policy")


@pytest.mark.asyncio
async def test_assistant_does_not_call_llm_without_authorized_evidence() -> None:
    retrieval = StubRetrieval([])
    provider = DeterministicGroundedProvider("This must never be returned.")
    service = AssistantService(retrieval=retrieval, provider=provider)  # type: ignore[arg-type]
    principal = Principal(uuid.uuid4(), uuid.uuid4(), Role.ANALYST)

    result = await service.answer(principal, "What is the policy?")

    assert result.model == "no-evidence"
    assert "could not find authorized source material" in result.answer
    assert result.grounding.grounded is False
    assert provider.requests == []

