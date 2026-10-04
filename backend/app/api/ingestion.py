from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.embeddings.base import EmbeddingProvider
from app.embeddings.dependencies import get_embedding_provider
from app.ingestion.chunking import SectionAwareChunker
from app.ingestion.domain import IngestionMetadata, IngestionSource
from app.ingestion.parsers import UnsupportedDocumentError
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.repository import SqlAlchemyIngestionRepository
from app.schemas.ingestion import IngestedChunkResponse, IngestionResponse
from app.security.dependencies import require_permission
from app.security.principal import Permission, Principal, Role

router = APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])


async def get_ingestion_pipeline(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    embeddings: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
) -> IngestionPipeline:
    return IngestionPipeline(
        SqlAlchemyIngestionRepository(session),
        chunker=SectionAwareChunker(
            max_words=settings.chunk_size_words,
            overlap_words=settings.chunk_overlap_words,
        ),
        embedding_provider=embeddings,
    )


DocumentWriter = Annotated[
    Principal,
    Depends(require_permission(Permission.DOCUMENTS_WRITE)),
]
PipelineDependency = Annotated[IngestionPipeline, Depends(get_ingestion_pipeline)]
SettingsDependency = Annotated[Settings, Depends(get_settings)]


@router.post("/documents", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    principal: DocumentWriter,
    pipeline: PipelineDependency,
    settings: SettingsDependency,
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form(min_length=3, max_length=300)],
    version: Annotated[str, Form(min_length=1, max_length=80)],
    source_type: Annotated[str, Form(min_length=2, max_length=40)] = "policy",
    classification: Annotated[str, Form(min_length=2, max_length=40)] = "internal",
    product: Annotated[str | None, Form(max_length=100)] = None,
    effective_date: Annotated[date | None, Form()] = None,
    allowed_roles: Annotated[str, Form()] = "viewer,analyst,compliance,admin",
) -> IngestionResponse:
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Document exceeds configured upload limit")
    try:
        roles = tuple(Role(value.strip()) for value in allowed_roles.split(",") if value.strip())
        if not roles:
            raise ValueError("at least one allowed role is required")
        result = await pipeline.ingest(
            tenant_id=principal.tenant_id,
            source=IngestionSource(filename=file.filename or "document.txt", content=content),
            metadata=IngestionMetadata(
                title=title,
                version=version,
                source_type=source_type,
                classification=classification,
                product=product,
                effective_date=effective_date,
                allowed_roles=roles,
            ),
        )
    except (UnsupportedDocumentError, UnicodeDecodeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return IngestionResponse(
        document_id=result.document_id,
        status=result.status,
        source_sha256=result.source_sha256,
        chunks=[
            IngestedChunkResponse(
                ordinal=chunk.ordinal,
                section=chunk.section,
                page_number=chunk.page_number,
                token_count=chunk.token_count,
            )
            for chunk in result.chunks
        ],
    )
