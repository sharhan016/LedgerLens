from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContextSource:
    source_id: str
    chunk_id: str
    document_id: str
    title: str
    source: str
    version: str
    content: str
    section: str | None
    page_number: int | None


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    question: str
    context: str
    sources: tuple[ContextSource, ...]
    intent: str


@dataclass(frozen=True, slots=True)
class LLMGeneration:
    answer: str
    cited_source_ids: tuple[str, ...]
    model: str


@dataclass(frozen=True, slots=True)
class GroundingReport:
    grounded: bool
    citation_coverage: float
    lexical_support: float
    confidence: float
    unsupported_claims: tuple[str, ...]
    invalid_citations: tuple[str, ...]

