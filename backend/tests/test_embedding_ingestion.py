import uuid

import pytest

from app.embeddings.deterministic import DeterministicHashEmbeddingProvider
from app.ingestion.domain import IngestionMetadata, IngestionSource
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.repository import InMemoryIngestionRepository
from app.security.principal import Role


@pytest.mark.asyncio
async def test_ingestion_embeds_each_chunk_with_configured_provider() -> None:
    repository = InMemoryIngestionRepository()
    pipeline = IngestionPipeline(
        repository,
        embedding_provider=DeterministicHashEmbeddingProvider(dimensions=24),
    )
    result = await pipeline.ingest(
        tenant_id=uuid.uuid4(),
        source=IngestionSource("policy.txt", b"Synthetic minimum balance policy."),
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

    assert len(result.chunks) == 1
    assert result.chunks[0].embedding is not None
    assert len(result.chunks[0].embedding or ()) == 24

