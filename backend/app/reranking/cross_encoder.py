import asyncio
from dataclasses import replace
from functools import partial

from app.embeddings.sentence_transformers import MissingMLDependencyError
from app.retrieval.domain import RetrievalCandidate


class CrossEncoderReranker:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model = None

    def _load_model(self):  # type: ignore[no-untyped-def]
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
            except ImportError as error:
                raise MissingMLDependencyError(
                    "install LedgerLens with the 'ml' extra to use cross-encoder reranking"
                ) from error
            self._model = CrossEncoder(self._model_name)
        return self._model

    def _rerank_sync(
        self, query: str, candidates: list[RetrievalCandidate]
    ) -> list[RetrievalCandidate]:
        if not candidates:
            return []
        scores = self._load_model().predict([(query, item.content) for item in candidates])
        reranked = [
            replace(candidate, rerank_score=float(score))
            for candidate, score in zip(candidates, scores, strict=True)
        ]
        return sorted(reranked, key=lambda item: item.rerank_score or 0.0, reverse=True)

    async def rerank(
        self, query: str, candidates: list[RetrievalCandidate]
    ) -> list[RetrievalCandidate]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(self._rerank_sync, query, candidates))

