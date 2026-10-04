import uuid

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)


class RetrievalPassageResponse(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    title: str
    source: str
    version: str
    content: str
    section: str | None
    page_number: int | None
    dense_score: float | None
    keyword_score: float | None
    rrf_score: float
    rerank_score: float | None


class RetrievalResponse(BaseModel):
    query: str
    passages: list[RetrievalPassageResponse]

