from typing import Annotated

from fastapi import APIRouter, Depends

from app.retrieval.dependencies import get_retrieval_orchestrator
from app.retrieval.orchestrator import HybridRetrievalOrchestrator
from app.schemas.retrieval import RetrievalPassageResponse, RetrievalRequest, RetrievalResponse
from app.security.dependencies import require_permission
from app.security.principal import Permission, Principal

router = APIRouter(prefix="/api/v1/retrieval", tags=["retrieval"])

DocumentReader = Annotated[
    Principal,
    Depends(require_permission(Permission.DOCUMENTS_READ)),
]
RetrievalDependency = Annotated[
    HybridRetrievalOrchestrator,
    Depends(get_retrieval_orchestrator),
]


@router.post("/search", response_model=RetrievalResponse)
async def retrieve(
    request: RetrievalRequest,
    principal: DocumentReader,
    orchestrator: RetrievalDependency,
) -> RetrievalResponse:
    passages = await orchestrator.search(principal, request.query)
    return RetrievalResponse(
        query=request.query,
        passages=[
            RetrievalPassageResponse(
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                title=item.title,
                source=item.source,
                version=item.version,
                content=item.content,
                section=item.section,
                page_number=item.page_number,
                dense_score=item.dense_score,
                keyword_score=item.keyword_score,
                rrf_score=item.rrf_score,
                rerank_score=item.rerank_score,
            )
            for item in passages
        ],
    )

