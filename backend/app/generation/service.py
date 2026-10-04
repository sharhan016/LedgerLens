import hashlib
import time
import uuid
from dataclasses import dataclass

from app.embeddings.base import EmbeddingProvider
from app.generation.context import ContextBuilder
from app.generation.domain import ContextSource, GenerationRequest, GroundingReport, LLMGeneration
from app.generation.grounding import GroundingValidator
from app.generation.providers import LLMProvider
from app.generation.query import QueryPlan, RuleBasedQueryPlanner
from app.operations.ports import (
    AuditSink,
    ConversationRecorder,
    GenerationCache,
    KnowledgeVersionProvider,
)
from app.retrieval.domain import RetrievalCandidate
from app.retrieval.ports import RetrievalOrchestrator
from app.security.principal import Principal


@dataclass(frozen=True, slots=True)
class AssistantResult:
    answer: str
    model: str
    plan: QueryPlan
    sources: tuple[ContextSource, ...]
    passages: tuple[RetrievalCandidate, ...]
    grounding: GroundingReport
    latency_ms: dict[str, float]
    conversation_id: uuid.UUID | None
    cache_hit: bool


class AssistantService:
    def __init__(
        self,
        *,
        retrieval: RetrievalOrchestrator,
        provider: LLMProvider,
        planner: RuleBasedQueryPlanner | None = None,
        context_builder: ContextBuilder | None = None,
        validator: GroundingValidator | None = None,
        cache: GenerationCache | None = None,
        cache_embeddings: EmbeddingProvider | None = None,
        knowledge_versions: KnowledgeVersionProvider | None = None,
        conversations: ConversationRecorder | None = None,
        audit: AuditSink | None = None,
    ) -> None:
        self._retrieval = retrieval
        self._provider = provider
        self._planner = planner or RuleBasedQueryPlanner()
        self._context_builder = context_builder or ContextBuilder()
        self._validator = validator or GroundingValidator()
        self._cache = cache
        self._cache_embeddings = cache_embeddings
        self._knowledge_versions = knowledge_versions
        self._conversations = conversations
        self._audit = audit

    async def answer(
        self,
        principal: Principal,
        question: str,
        *,
        conversation_id: uuid.UUID | None = None,
    ) -> AssistantResult:
        started = time.perf_counter()
        plan = self._planner.plan(question)
        planned = time.perf_counter()
        passages = await self._retrieval.search(
            principal,
            plan.retrieval_query,
            route=plan.route,
        )
        retrieved = time.perf_counter()
        context, sources = self._context_builder.build(passages)
        cache_hit = False
        if not sources:
            generation_answer = "I could not find authorized source material for this question."
            generation = LLMGeneration(generation_answer, (), "no-evidence")
        else:
            generation = None
            cache_context: tuple[list[float], str, str] | None = None
            if self._cache and self._cache_embeddings and self._knowledge_versions:
                query_embedding = (await self._cache_embeddings.embed([plan.retrieval_query]))[0]
                knowledge_version = await self._knowledge_versions.get(principal.tenant_id)
                context_fingerprint = hashlib.sha256(
                    "|".join(f"{source.chunk_id}:{source.version}" for source in sources).encode()
                ).hexdigest()
                cache_context = (query_embedding, knowledge_version, context_fingerprint)
                generation = await self._cache.get(
                    tenant_id=principal.tenant_id,
                    role=principal.role,
                    query_embedding=query_embedding,
                    knowledge_version=knowledge_version,
                    context_fingerprint=context_fingerprint,
                )
                cache_hit = generation is not None
            if generation is None:
                generation = await self._provider.generate(
                    GenerationRequest(
                        question=plan.original_query,
                        context=context,
                        sources=sources,
                        intent=plan.intent.value,
                    )
                )
                if cache_context and self._cache:
                    query_embedding, knowledge_version, context_fingerprint = cache_context
                    await self._cache.put(
                        tenant_id=principal.tenant_id,
                        role=principal.role,
                        query=plan.retrieval_query,
                        query_embedding=query_embedding,
                        knowledge_version=knowledge_version,
                        context_fingerprint=context_fingerprint,
                        generation=generation,
                    )
        generated = time.perf_counter()
        retrieval_quality = (
            sum((item.rerank_score or 0.0) for item in passages) / len(passages)
            if passages
            else 0.0
        )
        grounding = self._validator.validate(
            generation,
            sources,
            retrieval_quality=max(0.0, min(1.0, retrieval_quality)),
        )
        validated = time.perf_counter()
        resolved_conversation_id = conversation_id
        if self._conversations:
            resolved_conversation_id = await self._conversations.record_exchange(
                principal=principal,
                conversation_id=conversation_id,
                question=plan.original_query,
                answer=generation.answer,
                metadata={
                    "model": generation.model,
                    "route": plan.route,
                    "grounded": grounding.grounded,
                    "confidence": grounding.confidence,
                    "source_ids": list(generation.cited_source_ids),
                    "cache_hit": cache_hit,
                },
            )
        if self._audit:
            await self._audit.record(
                principal=principal,
                action="assistant.answer",
                resource_type="conversation",
                resource_id=str(resolved_conversation_id) if resolved_conversation_id else None,
                details={
                    "question_sha256": hashlib.sha256(plan.original_query.encode()).hexdigest(),
                    "route": plan.route,
                    "grounded": grounding.grounded,
                    "confidence": grounding.confidence,
                    "cache_hit": cache_hit,
                    "source_count": len(sources),
                },
            )
        finished = time.perf_counter()
        latency_ms = {
            "planning": round((planned - started) * 1000, 3),
            "retrieval": round((retrieved - planned) * 1000, 3),
            "generation": round((generated - retrieved) * 1000, 3),
            "validation": round((validated - generated) * 1000, 3),
            "operations": round((finished - validated) * 1000, 3),
            "total": round((finished - started) * 1000, 3),
        }
        return AssistantResult(
            answer=generation.answer,
            model=generation.model,
            plan=plan,
            sources=sources,
            passages=tuple(passages),
            grounding=grounding,
            latency_ms=latency_ms,
            conversation_id=resolved_conversation_id,
            cache_hit=cache_hit,
        )
