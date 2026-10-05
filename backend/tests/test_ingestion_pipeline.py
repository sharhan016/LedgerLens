import uuid
from datetime import date

import pytest

from app.ingestion.boundaries import (
    DEFAULT_PROCESSING_SEGMENT_BYTES,
    Utf8ProcessingBoundary,
)
from app.ingestion.chunking import SectionAwareChunker
from app.ingestion.cleaning import clean_content
from app.ingestion.domain import IngestionMetadata, IngestionSource, SourceSegment
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
    chunker = SectionAwareChunker(max_words=20, overlap_words=4)
    text = "  ".join(f"word-{index}" for index in range(45))

    chunks = chunker.chunk((SourceSegment(text, section="Rules", page_number=7),))

    assert len(chunks) == 3
    assert chunks[0].content.split()[-4:] == chunks[1].content.split()[:4]
    assert all(chunk.page_number == 7 for chunk in chunks)
    assert all("  " not in chunk.content for chunk in chunks)


def test_processing_boundary_limits_cleaned_utf8_bytes_and_preserves_location() -> None:
    boundary = Utf8ProcessingBoundary(max_bytes=8)
    original = SourceSegment("\x00éé  ééé", section="Eligibility", page_number=7)

    segments = boundary.split((original,))

    assert len(segments) == 2
    assert all(len(segment.content.encode("utf-8")) <= 8 for segment in segments)
    assert "".join(segment.content for segment in segments) == clean_content(original.content)
    assert all(segment.section == "Eligibility" for segment in segments)
    assert all(segment.page_number == 7 for segment in segments)


def test_default_processing_boundary_is_512_kib() -> None:
    content = "a" * (DEFAULT_PROCESSING_SEGMENT_BYTES + 1)

    segments = Utf8ProcessingBoundary().split((SourceSegment(content),))

    assert [len(segment.content.encode("utf-8")) for segment in segments] == [
        DEFAULT_PROCESSING_SEGMENT_BYTES,
        1,
    ]


def test_default_semantic_chunks_remain_180_words_with_30_word_overlap() -> None:
    words = [f"word-{index}" for index in range(400)]

    chunks = SectionAwareChunker().chunk((SourceSegment(" ".join(words)),))

    assert [len(chunk.content.split()) for chunk in chunks] == [180, 180, 100]
    assert chunks[0].content.split()[-30:] == chunks[1].content.split()[:30]
    assert chunks[1].content.split()[-30:] == chunks[2].content.split()[:30]


@pytest.mark.asyncio
async def test_pipeline_applies_processing_boundary_before_semantic_chunking() -> None:
    class RecordingChunker(SectionAwareChunker):
        received_segments: tuple[SourceSegment, ...] = ()

        def chunk(self, segments: tuple[SourceSegment, ...]):  # type: ignore[no-untyped-def]
            self.received_segments = segments
            return super().chunk(segments)

    repository = InMemoryIngestionRepository()
    chunker = RecordingChunker(max_words=20, overlap_words=5)
    pipeline = IngestionPipeline(
        repository,
        processing_boundary=Utf8ProcessingBoundary(max_bytes=16),
        chunker=chunker,
    )

    await pipeline.ingest(
        tenant_id=uuid.uuid4(),
        source=IngestionSource("policy.txt", b"alpha beta gamma delta epsilon zeta"),
        metadata=IngestionMetadata(
            title="Policy",
            version="1",
            source_type="policy",
            classification="internal",
            product=None,
            effective_date=None,
            allowed_roles=(Role.ANALYST,),
        ),
    )

    assert len(chunker.received_segments) == 3
    assert all(
        len(segment.content.encode("utf-8")) <= 16
        for segment in chunker.received_segments
    )
