import asyncio

from app.embeddings.base import EmbeddingProvider
from app.reranking.base import Reranker
from app.retrieval.domain import RetrievalCandidate
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.ports import DenseRetriever, KeywordRetriever
from app.security.principal import Permission, Principal


class RetrievalPermissionError(RuntimeError):
    pass


class HybridRetrievalOrchestrator:
    def __init__(
        self,
        *,
        embeddings: EmbeddingProvider,
        dense: DenseRetriever,
        keyword: KeywordRetriever,
        reranker: Reranker,
        candidate_limit: int = 30,
        result_limit: int = 8,
        rrf_constant: int = 60,
    ) -> None:
        self._embeddings = embeddings
        self._dense = dense
        self._keyword = keyword
        self._reranker = reranker
        self._candidate_limit = candidate_limit
        self._result_limit = result_limit
        self._rrf_constant = rrf_constant

    async def search(self, principal: Principal, query: str) -> list[RetrievalCandidate]:
        if not principal.can(Permission.DOCUMENTS_READ):
            raise RetrievalPermissionError("documents:read permission required")
        normalized_query = " ".join(query.split())
        if len(normalized_query) < 3:
            raise ValueError("query must contain at least three characters")
        vectors = await self._embeddings.embed([normalized_query])
        if len(vectors) != 1:
            raise ValueError("embedding provider did not return one query vector")
        dense_results, keyword_results = await asyncio.gather(
            self._dense.search(
                tenant_id=principal.tenant_id,
                role=principal.role,
                embedding=vectors[0],
                limit=self._candidate_limit,
            ),
            self._keyword.search(
                tenant_id=principal.tenant_id,
                role=principal.role,
                query=normalized_query,
                limit=self._candidate_limit,
            ),
        )
        # PostgreSQL applies these predicates before ranking. Keep a fail-closed guard at
        # orchestration so a future adapter cannot accidentally bypass the invariant.
        authorized_dense = [
            item
            for item in dense_results
            if item.tenant_id == principal.tenant_id and principal.role.value in item.allowed_roles
        ]
        authorized_keyword = [
            item
            for item in keyword_results
            if item.tenant_id == principal.tenant_id and principal.role.value in item.allowed_roles
        ]
        fused = reciprocal_rank_fusion(
            authorized_dense,
            authorized_keyword,
            constant=self._rrf_constant,
        )
        reranked = await self._reranker.rerank(
            normalized_query,
            fused[: self._candidate_limit],
        )
        return reranked[: self._result_limit]

