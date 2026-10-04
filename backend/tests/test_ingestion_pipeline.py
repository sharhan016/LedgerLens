import uuid
from datetime import date

import pytest

from app.ingestion.chunking import SectionAwareChunker
from app.ingestion.domain import IngestionMetadata, IngestionSource
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.repository import InMemoryIngestionRepository
from app.security.principal import Role


@pytest.mark.asyncio
async def test_pipeline_preserves_traceability_and_authorization_metadata() -> None:
    repository = InMemoryIngestionRepository()
    pipeline = IngestionPipeline(
        repository,
        chunker=SectionAwareChunker(max_words=20, overlap_words=5),
    )
    tenant_id = uuid.uuid4()
    source = IngestionSource(
        filename="policy.md",
        content=(
            b"---\nsynthetic: true\n---\n# Eligibility\n"
            b"Applicants must complete identity checks before account activation. "
            b"The policy applies to the fictional demonstration environment only."
        ),
    )
    metadata = IngestionMetadata(
        title="Synthetic Policy",
        version="2026.1",
        source_type="policy",
        classification="internal",
        product="demo",
        effective_date=date(2026, 1, 1),
        allowed_roles=(Role.ANALYST, Role.COMPLIANCE),
    )

    result = await pipeline.ingest(tenant_id=tenant_id, source=source, metadata=metadata)

    assert result.status == "ready"
    assert len(result.source_sha256) == 64
    assert result.chunks
    assert [chunk.ordinal for chunk in result.chunks] == list(range(len(result.chunks)))
    assert all(chunk.section == "Eligibility" for chunk in result.chunks)
    assert all(chunk.metadata["source"] == "policy.md" for chunk in result.chunks)
    assert all(chunk.metadata["version"] == "2026.1" for chunk in result.chunks)
    assert all(chunk.metadata["tenant_id"] == str(tenant_id) for chunk in result.chunks)
    assert all(
        chunk.metadata["allowed_roles"] == ["analyst", "compliance"]
        for chunk in result.chunks
    )
    stored = repository.documents[result.document_id]
    assert stored["tenant_id"] == tenant_id
    assert stored["status"] == "ready"


def test_chunker_cleans_content_and_adds_bounded_overlap() -> None:
    from app.ingestion.domain import SourceSegment

    chunker = SectionAwareChunker(max_words=20, overlap_words=4)
    text = "  ".join(f"word-{index}" for index in range(45))

    chunks = chunker.chunk((SourceSegment(text, section="Rules", page_number=7),))

    assert len(chunks) == 3
    assert chunks[0].content.split()[-4:] == chunks[1].content.split()[:4]
    assert all(chunk.page_number == 7 for chunk in chunks)
    assert all("  " not in chunk.content for chunk in chunks)

