from typing import Annotated

from fastapi import APIRouter, Depends

from app.generation.service import AssistantService
from app.generation.service_dependencies import get_assistant_service
from app.schemas.assistant import (
    AskRequest,
    AssistantResponse,
    CitationResponse,
    GroundingResponse,
    PassageEvidenceResponse,
    QueryTraceResponse,
)
from app.security.dependencies import require_permission
from app.security.principal import Permission, Principal

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])

DocumentReader = Annotated[
    Principal,
    Depends(require_permission(Permission.DOCUMENTS_READ)),
]
AssistantDependency = Annotated[AssistantService, Depends(get_assistant_service)]


@router.post("/ask", response_model=AssistantResponse)
async def ask(
    request: AskRequest,
    principal: DocumentReader,
    assistant: AssistantDependency,
) -> AssistantResponse:
    result = await assistant.answer(principal, request.question)
    return AssistantResponse(
        answer=result.answer,
        model=result.model,
        citations=[
            CitationResponse(
                source_id=source.source_id,
                document_id=source.document_id,
                chunk_id=source.chunk_id,
                title=source.title,
                source=source.source,
                version=source.version,
                section=source.section,
                page_number=source.page_number,
                excerpt=source.content[:360],
            )
            for source in result.sources
        ],
        passages=[
            PassageEvidenceResponse(
                chunk_id=passage.chunk_id,
                title=passage.title,
                source=passage.source,
                content=passage.content,
                section=passage.section,
                page_number=passage.page_number,
                dense_score=passage.dense_score,
                keyword_score=passage.keyword_score,
                rrf_score=passage.rrf_score,
                rerank_score=passage.rerank_score,
            )
            for passage in result.passages
        ],
        grounding=GroundingResponse(
            grounded=result.grounding.grounded,
            citation_coverage=result.grounding.citation_coverage,
            lexical_support=result.grounding.lexical_support,
            confidence=result.grounding.confidence,
            unsupported_claims=list(result.grounding.unsupported_claims),
            invalid_citations=list(result.grounding.invalid_citations),
        ),
        query_trace=QueryTraceResponse(
            original_query=result.plan.original_query,
            retrieval_query=result.plan.retrieval_query,
            intent=result.plan.intent.value,
            route=result.plan.route,
            transformations=list(result.plan.transformations),
        ),
        latency_ms=result.latency_ms,
    )

