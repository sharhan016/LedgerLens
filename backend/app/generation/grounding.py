import re

from app.generation.domain import ContextSource, GroundingReport, LLMGeneration

CITATION_PATTERN = re.compile(r"\[(S\d+)\]")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def _tokens(value: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(value) if len(token) > 2}


class GroundingValidator:
    def validate(
        self,
        generation: LLMGeneration,
        sources: tuple[ContextSource, ...],
        *,
        retrieval_quality: float,
    ) -> GroundingReport:
        source_map = {source.source_id: source for source in sources}
        declared = set(generation.cited_source_ids)
        inline = set(CITATION_PATTERN.findall(generation.answer))
        all_citations = declared | inline
        invalid = tuple(sorted(all_citations - source_map.keys()))
        claims = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", generation.answer)
            if len(_tokens(sentence)) >= 3
        ]
        supported = 0
        cited = 0
        unsupported: list[str] = []
        for claim in claims:
            markers = CITATION_PATTERN.findall(claim)
            valid_markers = [marker for marker in markers if marker in source_map]
            if valid_markers:
                cited += 1
            claim_tokens = _tokens(CITATION_PATTERN.sub("", claim))
            source_tokens = set().union(
                *(_tokens(source_map[marker].content) for marker in valid_markers)
            ) if valid_markers else set()
            overlap = len(claim_tokens & source_tokens) / (len(claim_tokens) or 1)
            if valid_markers and overlap >= 0.25:
                supported += 1
            else:
                unsupported.append(claim)
        denominator = len(claims) or 1
        coverage = cited / denominator
        lexical_support = supported / denominator
        confidence = max(
            0.0,
            min(1.0, 0.45 * coverage + 0.35 * lexical_support + 0.20 * retrieval_quality),
        )
        grounded = bool(claims) and not invalid and not unsupported
        return GroundingReport(
            grounded=grounded,
            citation_coverage=round(coverage, 4),
            lexical_support=round(lexical_support, 4),
            confidence=round(confidence, 4),
            unsupported_claims=tuple(unsupported),
            invalid_citations=invalid,
        )

