from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.embeddings.base import EmbeddingProvider
from app.embeddings.dependencies import get_embedding_provider
from app.generation.context import ContextBuilder
from app.generation.dependencies import get_llm_provider
from app.generation.providers import LLMProvider
from app.generation.service import AssistantService
from app.operations.postgres import (
    PostgresAuditSink,
    PostgresConversationRecorder,
    PostgresGenerationCache,
    PostgresKnowledgeVersionProvider,
)
from app.retrieval.dependencies import get_retrieval_orchestrator
from app.retrieval.ports import RetrievalOrchestrator


async def get_assistant_service(
    retrieval: Annotated[RetrievalOrchestrator, Depends(get_retrieval_orchestrator)],
    provider: Annotated[LLMProvider, Depends(get_llm_provider)],
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_session)],
    embeddings: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
) -> AssistantService:
    return AssistantService(
        retrieval=retrieval,
        provider=provider,
        context_builder=ContextBuilder(max_characters=settings.context_max_characters),
        cache=PostgresGenerationCache(
            session,
            similarity_threshold=settings.semantic_cache_similarity_threshold,
            ttl_minutes=settings.semantic_cache_ttl_minutes,
        ),
        cache_embeddings=embeddings,
        knowledge_versions=PostgresKnowledgeVersionProvider(session),
        conversations=PostgresConversationRecorder(session),
        audit=PostgresAuditSink(session),
    )
