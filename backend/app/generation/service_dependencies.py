from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.generation.context import ContextBuilder
from app.generation.dependencies import get_llm_provider
from app.generation.providers import LLMProvider
from app.generation.service import AssistantService
from app.retrieval.dependencies import get_retrieval_orchestrator
from app.retrieval.ports import RetrievalOrchestrator


async def get_assistant_service(
    retrieval: Annotated[RetrievalOrchestrator, Depends(get_retrieval_orchestrator)],
    provider: Annotated[LLMProvider, Depends(get_llm_provider)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AssistantService:
    return AssistantService(
        retrieval=retrieval,
        provider=provider,
        context_builder=ContextBuilder(max_characters=settings.context_max_characters),
    )
