from typing import Protocol

from app.retrieval.domain import RetrievalCandidate


class Reranker(Protocol):
    async def rerank(
        self, query: str, candidates: list[RetrievalCandidate]
    ) -> list[RetrievalCandidate]: ...

