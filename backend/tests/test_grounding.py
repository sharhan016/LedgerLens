from app.generation.domain import ContextSource, LLMGeneration
from app.generation.grounding import GroundingValidator


def source(source_id: str, content: str) -> ContextSource:
    return ContextSource(
        source_id=source_id,
        chunk_id="00000000-0000-0000-0000-000000000001",
        document_id="00000000-0000-0000-0000-000000000002",
        title="Policy",
        source="policy.md",
        version="1",
        content=content,
        section="Rules",
        page_number=None,
    )


def test_validator_accepts_supported_cited_claim() -> None:
    report = GroundingValidator().validate(
        LLMGeneration(
            "The required average monthly balance is INR 25,000 [S1].",
            ("S1",),
            "test",
        ),
        (source("S1", "The account requires an average monthly balance of INR 25,000."),),
        retrieval_quality=0.9,
    )

    assert report.grounded is True
    assert report.citation_coverage == 1.0
    assert report.lexical_support == 1.0
    assert report.confidence > 0.9


def test_validator_labels_uncited_and_unknown_source_claims() -> None:
    report = GroundingValidator().validate(
        LLMGeneration(
            "The fee is always waived. A manager must approve it [S9].",
            ("S9",),
            "test",
        ),
        (source("S1", "The shortfall fee is INR 350."),),
        retrieval_quality=0.8,
    )

    assert report.grounded is False
    assert report.invalid_citations == ("S9",)
    assert len(report.unsupported_claims) == 2

