from functools import lru_cache

from app.core.config import get_settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.deterministic import DeterministicHashEmbeddingProvider
from app.embeddings.sentence_transformers import SentenceTransformerEmbeddingProvider


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.ml_mode == "deterministic_demo":
        return DeterministicHashEmbeddingProvider(dimensions=settings.embedding_dimensions)
    return SentenceTransformerEmbeddingProvider(
        settings.embedding_model,
        dimensions=settings.embedding_dimensions,
    )
