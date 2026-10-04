import uuid

from pydantic import BaseModel


class IngestedChunkResponse(BaseModel):
    ordinal: int
    section: str | None
    page_number: int | None
    token_count: int


class IngestionResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    source_sha256: str
    chunks: list[IngestedChunkResponse]

