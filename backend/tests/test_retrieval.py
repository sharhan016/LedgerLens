import uuid

import pytest

from app.embeddings.deterministic import DeterministicHashEmbeddingProvider
from app.reranking.deterministic import TokenOverlapReranker
from app.retrieval.domain import RetrievalCandidate
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.orchestrator import HybridRetrievalOrchestrator
from app.security.principal import Principal, Role


def candidate(
    *,
    tenant_id: uuid.UUID,
    title: str,
    content: str,
    roles: tuple[str, ...] = ("analyst",),
    chunk_id: uuid.UUID | None = None,
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=chunk_id or uuid.uuid4(),
        document_id=uuid.uuid4(),
        tenant_id=tenant_id,
        title=title,
        source=f"{title.lower().replace(' ', '-')}.md",
        version="2026.1",
        content=content,
        section="Eligibility",
        page_number=None,
        allowed_roles=roles,
    )


class FakeDenseRetriever:
    def __init__(self, results: list[RetrievalCandidate]) -> None:
        self.results = results
        self.calls: list[tuple[uuid.UUID, Role, int]] = []

    async def search(self, *, tenant_id, role, embedding, limit):  # type: ignore[no-untyped-def]
        self.calls.append((tenant_id, role, limit))
        return [
            item.with_rank(channel="dense", rank=index, score=1.0 / index)
            for index, item in enumerate(self.results, start=1)
        ]


class FakeKeywordRetriever:
    def __init__(self, results: list[RetrievalCandidate]) -> None:
        self.results = results
        self.calls: list[tuple[uuid.UUID, Role, str, int]] = []

    async def search(self, *, tenant_id, role, query, limit):  # type: ignore[no-untyped-def]
        self.calls.append((tenant_id, role, query, limit))
        return [
            item.with_rank(channel="keyword", rank=index, score=1.0 / index)
            for index, item in enumerate(self.results, start=1)
        ]


def test_rrf_rewards_candidates_found_by_both_channels() -> None:
    tenant_id = uuid.uuid4()
    shared_id = uuid.uuid4()
    shared = candidate(
        tenant_id=tenant_id,
        title="Shared",
        content="minimum premium balance",
        chunk_id=shared_id,
    )
    dense_only = candidate(tenant_id=tenant_id, title="Dense", content="semantic match")
    keyword_only = candidate(tenant_id=tenant_id, title="Keyword", content="exact match")

    fused = reciprocal_rank_fusion(
        [dense_only, shared],
        [keyword_only, shared],
        constant=60,
    )

    assert fused[0].chunk_id == shared_id
    assert fused[0].dense_rank == 2
    assert fused[0].keyword_rank == 2
    assert fused[0].rrf_score == pytest.approx(2 / 62)


@pytest.mark.asyncio
async def test_orchestrator_filters_unauthorized_results_before_reranking() -> None:
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    authorized = candidate(
        tenant_id=tenant_id,
        title="Savings",
        content="premium savings minimum balance is twenty five thousand",
    )
    cross_tenant = candidate(
        tenant_id=other_tenant,
        title="Foreign",
        content="premium savings minimum balance",
    )
    wrong_role = candidate(
        tenant_id=tenant_id,
        title="Restricted",
        content="premium balance",
        roles=("compliance",),
    )
    dense = FakeDenseRetriever([cross_tenant, authorized])
    keyword = FakeKeywordRetriever([wrong_role, authorized])
    orchestrator = HybridRetrievalOrchestrator(
        embeddings=DeterministicHashEmbeddingProvider(),
        dense=dense,
        keyword=keyword,
        reranker=TokenOverlapReranker(),
        result_limit=5,
    )
    principal = Principal(uuid.uuid4(), tenant_id, Role.ANALYST)

    results = await orchestrator.search(principal, "premium savings minimum balance")

    assert [item.chunk_id for item in results] == [authorized.chunk_id]
    assert results[0].rerank_score == 1.0
    assert dense.calls[0][:2] == (tenant_id, Role.ANALYST)
    assert keyword.calls[0][:3] == (tenant_id, Role.ANALYST, "premium savings minimum balance")

