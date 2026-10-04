import uuid
from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class RetrievalCandidate:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    source: str
    version: str
    content: str
    section: str | None
    page_number: int | None
    allowed_roles: tuple[str, ...]
    dense_score: float | None = None
    keyword_score: float | None = None
    dense_rank: int | None = None
    keyword_rank: int | None = None
    rrf_score: float = 0.0
    rerank_score: float | None = None
    retrieval_channel: str = "hybrid"
    validation_status: str = "authorized"

    def with_rank(self, *, channel: str, rank: int, score: float) -> "RetrievalCandidate":
        if channel == "dense":
            return replace(self, dense_rank=rank, dense_score=score)
        if channel == "keyword":
            return replace(self, keyword_rank=rank, keyword_score=score)
        raise ValueError(f"unknown retrieval channel: {channel}")
