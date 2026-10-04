import re
from dataclasses import replace

from app.retrieval.domain import RetrievalCandidate


class TokenOverlapReranker:
    """Deterministic reranker for unit tests and offline evaluation fixtures."""

    async def rerank(
        self, query: str, candidates: list[RetrievalCandidate]
    ) -> list[RetrievalCandidate]:
        query_tokens = set(re.findall(r"\w+", query.lower()))
        scored = []
        for candidate in candidates:
            content_tokens = set(re.findall(r"\w+", candidate.content.lower()))
            denominator = len(query_tokens) or 1
            score = len(query_tokens & content_tokens) / denominator
            scored.append(replace(candidate, rerank_score=score))
        return sorted(scored, key=lambda item: item.rerank_score or 0.0, reverse=True)

