import uuid

import pytest

from app.embeddings.deterministic import DeterministicHashEmbeddingProvider
from app.generation.domain import LLMGeneration
from app.generation.providers import DeterministicGroundedProvider
from app.generation.service import AssistantService
from app.operations.memory import (
    InMemoryAuditSink,
    InMemoryConversationRecorder,
    InMemoryGenerationCache,
    StaticKnowledgeVersion,
)
from app.retrieval.domain import RetrievalCandidate
from app.security.principal import Principal, Role


class StubRetrieval:
    def __init__(self, candidate: RetrievalCandidate) -> None:
        self.candidate = candidate

    async def search(self, principal, query, *, route="hybrid_knowledge"):  # type: ignore[no-untyped-def]
        return [self.candidate]


def passage(tenant_id: uuid.UUID) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        tenant_id=tenant_id,
        title="Premium Savings Policy",
        source="premium-savings-policy.md",
        version="2026.2",
        content="The average monthly balance is INR 25,000.",
        section="Balance",
        page_number=None,
        allowed_roles=("analyst",),
        rerank_score=0.95,
    )


@pytest.mark.asyncio
async def test_semantic_cache_is_tenant_role_version_and_context_scoped() -> None:
    cache = InMemoryGenerationCache(similarity_threshold=0.9)
    tenant_id = uuid.uuid4()
    generation = LLMGeneration("Answer [S1].", ("S1",), "model")
    await cache.put(
        tenant_id=tenant_id,
        role=Role.ANALYST,
        query="question",
        query_embedding=[1.0, 0.0],
        knowledge_version="v1",
        context_fingerprint="context-a",
        generation=generation,
    )

    assert (
        await cache.get(
            tenant_id=tenant_id,
            role=Role.ANALYST,
            query_embedding=[0.99, 0.01],
            knowledge_version="v1",
            context_fingerprint="context-a",
        )
        == generation
    )
    for changed in (
        {"tenant_id": uuid.uuid4()},
        {"role": Role.COMPLIANCE},
        {"knowledge_version": "v2"},
        {"context_fingerprint": "context-b"},
    ):
        arguments = {
            "tenant_id": tenant_id,
            "role": Role.ANALYST,
            "query_embedding": [1.0, 0.0],
            "knowledge_version": "v1",
            "context_fingerprint": "context-a",
            **changed,
        }
        assert await cache.get(**arguments) is None


@pytest.mark.asyncio
async def test_assistant_reuses_safe_cache_records_converses_and_audits_without_content() -> None:
    tenant_id = uuid.uuid4()
    principal = Principal(uuid.uuid4(), tenant_id, Role.ANALYST)
    provider = DeterministicGroundedProvider(
        "The average monthly balance is INR 25,000 [S1]."
    )
    cache = InMemoryGenerationCache()
    versions = StaticKnowledgeVersion("v1")
    conversations = InMemoryConversationRecorder()
    audit = InMemoryAuditSink()
    service = AssistantService(
        retrieval=StubRetrieval(passage(tenant_id)),  # type: ignore[arg-type]
        provider=provider,
        cache=cache,
        cache_embeddings=DeterministicHashEmbeddingProvider(dimensions=24),
        knowledge_versions=versions,
        conversations=conversations,
        audit=audit,
    )

    first = await service.answer(principal, "What is the average monthly balance?")
    second = await service.answer(
        principal,
        "What is the average monthly balance?",
        conversation_id=first.conversation_id,
    )

    assert first.cache_hit is False and second.cache_hit is True
    assert len(provider.requests) == 1
    assert second.conversation_id == first.conversation_id
    assert len(conversations.exchanges) == 2
    assert len(audit.events) == 2
    details = audit.events[0]["details"]
    assert isinstance(details, dict)
    assert "question_sha256" in details
    assert "What is" not in str(details)

    versions.value = "v2"
    third = await service.answer(principal, "What is the average monthly balance?")
    assert third.cache_hit is False
    assert len(provider.requests) == 2

