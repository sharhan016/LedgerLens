import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repositories.documents import SqlAlchemyDocumentRepository
from app.schemas.documents import DocumentResponse
from app.security.dependencies import require_permission
from app.security.principal import Permission, Principal
from app.services.documents import DocumentService

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


async def get_document_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DocumentService:
    return DocumentService(SqlAlchemyDocumentRepository(session))


DocumentReader = Annotated[
    Principal,
    Depends(require_permission(Permission.DOCUMENTS_READ)),
]
DocumentServiceDependency = Annotated[DocumentService, Depends(get_document_service)]


def present(record) -> DocumentResponse:  # type: ignore[no-untyped-def]
    return DocumentResponse(
        id=record.id,
        title=record.title,
        source_type=record.source_type,
        version=record.version,
        status=record.status,
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    principal: DocumentReader,
    service: DocumentServiceDependency,
) -> list[DocumentResponse]:
    records = await service.list_documents(principal)
    return [present(record) for record in records]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    principal: DocumentReader,
    service: DocumentServiceDependency,
) -> DocumentResponse:
    record = await service.get_document(principal, document_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return present(record)

