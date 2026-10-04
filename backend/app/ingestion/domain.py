import uuid
from dataclasses import dataclass, field
from datetime import date

from app.security.principal import Role


@dataclass(frozen=True, slots=True)
class SourceSegment:
    content: str
    section: str | None = None
    page_number: int | None = None


@dataclass(frozen=True, slots=True)
class IngestionMetadata:
    title: str
    version: str
    source_type: str
    classification: str
    product: str | None
    effective_date: date | None
    allowed_roles: tuple[Role, ...]


@dataclass(frozen=True, slots=True)
class IngestionSource:
    filename: str
    content: bytes


@dataclass(frozen=True, slots=True)
class PreparedChunk:
    ordinal: int
    content: str
    token_count: int
    section: str | None
    page_number: int | None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class IngestionResult:
    document_id: uuid.UUID
    status: str
    source_sha256: str
    chunks: tuple[PreparedChunk, ...]

