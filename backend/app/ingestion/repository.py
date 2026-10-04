import uuid
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.domain import IngestionMetadata, PreparedChunk
from app.models.entities import Chunk, Document


class IngestionRepository(Protocol):
    async def persist(
        self,
        *,
        tenant_id: uuid.UUID,
        source_key: str,
        source_sha256: str,
        metadata: IngestionMetadata,
        chunks: tuple[PreparedChunk, ...],
    ) -> uuid.UUID: ...


class SqlAlchemyIngestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def persist(
        self,
        *,
        tenant_id: uuid.UUID,
        source_key: str,
        source_sha256: str,
        metadata: IngestionMetadata,
        chunks: tuple[PreparedChunk, ...],
    ) -> uuid.UUID:
        document = Document(
            tenant_id=tenant_id,
            title=metadata.title,
            source_key=source_key,
            source_type=metadata.source_type,
            version=metadata.version,
            status="processing",
            allowed_roles=[role.value for role in metadata.allowed_roles],
            document_metadata={
                "classification": metadata.classification,
                "product": metadata.product,
                "effective_date": (
                    metadata.effective_date.isoformat() if metadata.effective_date else None
                ),
                "source_sha256": source_sha256,
            },
        )
        self._session.add(document)
        await self._session.flush()
        self._session.add_all(
            [
                Chunk(
                    tenant_id=tenant_id,
                    document_id=document.id,
                    ordinal=chunk.ordinal,
                    content=chunk.content,
                    section=chunk.section,
                    page_number=chunk.page_number,
                    token_count=chunk.token_count,
                    embedding=list(chunk.embedding) if chunk.embedding is not None else None,
                    chunk_metadata={
                        **chunk.metadata,
                        "source": source_key,
                        "version": metadata.version,
                        "classification": metadata.classification,
                        "allowed_roles": [role.value for role in metadata.allowed_roles],
                    },
                )
                for chunk in chunks
            ]
        )
        document.status = "ready"
        await self._session.commit()
        return document.id


class InMemoryIngestionRepository:
    def __init__(self) -> None:
        self.documents: dict[uuid.UUID, dict[str, object]] = {}

    async def persist(
        self,
        *,
        tenant_id: uuid.UUID,
        source_key: str,
        source_sha256: str,
        metadata: IngestionMetadata,
        chunks: tuple[PreparedChunk, ...],
    ) -> uuid.UUID:
        document_id = uuid.uuid4()
        self.documents[document_id] = {
            "tenant_id": tenant_id,
            "source_key": source_key,
            "source_sha256": source_sha256,
            "metadata": metadata,
            "chunks": chunks,
            "status": "ready",
        }
        return document_id
