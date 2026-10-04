from functools import lru_cache

from app.core.config import get_settings
from app.reranking.base import Reranker
from app.reranking.cross_encoder import CrossEncoderReranker
from app.reranking.deterministic import TokenOverlapReranker


@lru_cache
def get_reranker() -> Reranker:
    settings = get_settings()
    if settings.ml_mode == "deterministic_demo":
        return TokenOverlapReranker()
    return CrossEncoderReranker(settings.reranker_model)
