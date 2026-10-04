import hashlib
import uuid

from app.ingestion.chunking import SectionAwareChunker
from app.ingestion.domain import IngestionMetadata, IngestionResult, IngestionSource
from app.ingestion.parsers import ParserRegistry
from app.ingestion.repository import IngestionRepository


class IngestionPipeline:
    def __init__(
        self,
        repository: IngestionRepository,
        *,
        parsers: ParserRegistry | None = None,
        chunker: SectionAwareChunker | None = None,
    ) -> None:
        self._repository = repository
        self._parsers = parsers or ParserRegistry()
        self._chunker = chunker or SectionAwareChunker()

    async def ingest(
        self,
        *,
        tenant_id: uuid.UUID,
        source: IngestionSource,
        metadata: IngestionMetadata,
    ) -> IngestionResult:
        source_sha256 = hashlib.sha256(source.content).hexdigest()
        segments = self._parsers.parse(source)
        base_chunks = self._chunker.chunk(segments)
        chunks = tuple(
            type(chunk)(
                ordinal=chunk.ordinal,
                content=chunk.content,
                token_count=chunk.token_count,
                section=chunk.section,
                page_number=chunk.page_number,
                metadata={
                    "source": source.filename,
                    "version": metadata.version,
                    "tenant_id": str(tenant_id),
                    "allowed_roles": [role.value for role in metadata.allowed_roles],
                },
            )
            for chunk in base_chunks
        )
        document_id = await self._repository.persist(
            tenant_id=tenant_id,
            source_key=source.filename,
            source_sha256=source_sha256,
            metadata=metadata,
            chunks=chunks,
        )
        return IngestionResult(document_id, "ready", source_sha256, chunks)

