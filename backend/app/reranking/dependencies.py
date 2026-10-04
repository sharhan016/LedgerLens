from functools import lru_cache

from app.core.config import get_settings
from app.reranking.base import Reranker
from app.reranking.cross_encoder import CrossEncoderReranker


@lru_cache
def get_reranker() -> Reranker:
    return CrossEncoderReranker(get_settings().reranker_model)

