from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.embeddings.base import EmbeddingProvider
from app.embeddings.dependencies import get_embedding_provider
from app.reranking.base import Reranker
from app.reranking.dependencies import get_reranker
from app.retrieval.api_sources import (
    FixtureRegulatoryAdapter,
    HttpRegulatoryAdapter,
    RegulatoryRetriever,
)
from app.retrieval.orchestrator import HybridRetrievalOrchestrator
from app.retrieval.ports import RetrievalOrchestrator
from app.retrieval.postgres import PostgresDenseRetriever, PostgresKeywordRetriever
from app.retrieval.routed import RoutedRetrievalOrchestrator
from app.retrieval.structured import AllowlistedMetricRetriever


async def get_retrieval_orchestrator(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    embeddings: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
    reranker: Annotated[Reranker, Depends(get_reranker)],
) -> RetrievalOrchestrator:
    hybrid = HybridRetrievalOrchestrator(
        embeddings=embeddings,
        dense=PostgresDenseRetriever(session),
        keyword=PostgresKeywordRetriever(session),
        reranker=reranker,
        candidate_limit=settings.retrieval_candidate_limit,
        result_limit=settings.retrieval_result_limit,
        rrf_constant=settings.rrf_constant,
    )
    if settings.regulatory_api_mode == "fixture":
        adapter = FixtureRegulatoryAdapter(settings.regulatory_fixture_path)
    elif settings.regulatory_api_mode == "live" and settings.regulatory_api_url:
        adapter = HttpRegulatoryAdapter(
            settings.regulatory_api_url,
            timeout_seconds=settings.regulatory_api_timeout_seconds,
        )
    else:
        raise ValueError("regulatory API mode must be fixture or configured live")
    return RoutedRetrievalOrchestrator(
        hybrid=hybrid,
        structured=AllowlistedMetricRetriever(session),
        regulatory=RegulatoryRetriever(adapter),
        reranker=reranker,
        result_limit=settings.retrieval_result_limit,
    )
