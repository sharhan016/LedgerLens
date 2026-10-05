import hashlib
import uuid

from app.embeddings.base import EmbeddingProvider
from app.ingestion.boundaries import Utf8ProcessingBoundary
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
        processing_boundary: Utf8ProcessingBoundary | None = None,
        chunker: SectionAwareChunker | None = None,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        self._repository = repository
        self._parsers = parsers or ParserRegistry()
        self._processing_boundary = processing_boundary or Utf8ProcessingBoundary()
        self._chunker = chunker or SectionAwareChunker()
        self._embedding_provider = embedding_provider

    async def ingest(
        self,
        *,
        tenant_id: uuid.UUID,
        source: IngestionSource,
        metadata: IngestionMetadata,
    ) -> IngestionResult:
        source_sha256 = hashlib.sha256(source.content).hexdigest()
        segments = self._parsers.parse(source)
        bounded_segments = self._processing_boundary.split(segments)
        base_chunks = self._chunker.chunk(bounded_segments)
        embeddings = (
            await self._embedding_provider.embed([chunk.content for chunk in base_chunks])
            if self._embedding_provider is not None
            else [None] * len(base_chunks)
        )
        if len(embeddings) != len(base_chunks):
            raise ValueError("embedding provider returned an unexpected number of vectors")
        chunks = tuple(
            type(chunk)(
                ordinal=chunk.ordinal,
                content=chunk.content,
                token_count=chunk.token_count,
                section=chunk.section,
                page_number=chunk.page_number,
                embedding=(tuple(embedding) if embedding is not None else None),
                metadata={
                    "source": source.filename,
                    "version": metadata.version,
                    "tenant_id": str(tenant_id),
                    "allowed_roles": [role.value for role in metadata.allowed_roles],
                },
            )
            for chunk, embedding in zip(base_chunks, embeddings, strict=True)
        )
        document_id = await self._repository.persist(
            tenant_id=tenant_id,
            source_key=source.filename,
            source_sha256=source_sha256,
            metadata=metadata,
            chunks=chunks,
        )
        return IngestionResult(document_id, "ready", source_sha256, chunks)
