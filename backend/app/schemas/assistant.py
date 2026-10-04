import uuid

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    conversation_id: uuid.UUID | None = None


class CitationResponse(BaseModel):
    source_id: str
    document_id: uuid.UUID
    chunk_id: uuid.UUID
    title: str
    source: str
    version: str
    section: str | None
    page_number: int | None
    excerpt: str


class PassageEvidenceResponse(BaseModel):
    chunk_id: uuid.UUID
    title: str
    source: str
    content: str
    section: str | None
    page_number: int | None
    dense_score: float | None
    keyword_score: float | None
    rrf_score: float
    rerank_score: float | None
    retrieval_channel: str
    validation_status: str


class GroundingResponse(BaseModel):
    grounded: bool
    citation_coverage: float
    lexical_support: float
    confidence: float
    unsupported_claims: list[str]
    invalid_citations: list[str]


class QueryTraceResponse(BaseModel):
    original_query: str
    retrieval_query: str
    intent: str
    route: str
    transformations: list[str]
    routing_reason: str
    selected_sources: list[str]


class AssistantResponse(BaseModel):
    answer: str
    model: str
    citations: list[CitationResponse]
    passages: list[PassageEvidenceResponse]
    grounding: GroundingResponse
    query_trace: QueryTraceResponse
    latency_ms: dict[str, float]
    conversation_id: uuid.UUID | None
    cache_hit: bool
