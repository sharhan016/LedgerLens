from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.embeddings.base import EmbeddingProvider
from app.embeddings.dependencies import get_embedding_provider
from app.reranking.base import Reranker
from app.reranking.dependencies import get_reranker
from app.retrieval.orchestrator import HybridRetrievalOrchestrator
from app.retrieval.postgres import PostgresDenseRetriever, PostgresKeywordRetriever


async def get_retrieval_orchestrator(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    embeddings: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
    reranker: Annotated[Reranker, Depends(get_reranker)],
) -> HybridRetrievalOrchestrator:
    return HybridRetrievalOrchestrator(
        embeddings=embeddings,
        dense=PostgresDenseRetriever(session),
        keyword=PostgresKeywordRetriever(session),
        reranker=reranker,
        candidate_limit=settings.retrieval_candidate_limit,
        result_limit=settings.retrieval_result_limit,
        rrf_constant=settings.rrf_constant,
    )

