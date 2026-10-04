import uuid
from typing import Protocol

from app.reranking.base import Reranker
from app.retrieval.domain import RetrievalCandidate
from app.retrieval.ports import RetrievalOrchestrator
from app.security.principal import Principal, Role


class SupplementalRetriever(Protocol):
    async def search(
        self, *, tenant_id: uuid.UUID, role: Role, query: str, limit: int
    ) -> list[RetrievalCandidate]: ...


class RetrievalValidator:
    def validate(
        self, principal: Principal, candidates: list[RetrievalCandidate]
    ) -> list[RetrievalCandidate]:
        return [
            candidate
            for candidate in candidates
            if candidate.tenant_id == principal.tenant_id
            and principal.role.value in candidate.allowed_roles
            and bool(candidate.content.strip())
            and bool(candidate.source.strip())
        ]


class RoutedRetrievalOrchestrator:
    def __init__(
        self,
        *,
        hybrid: RetrievalOrchestrator,
        structured: SupplementalRetriever,
        regulatory: SupplementalRetriever,
        reranker: Reranker,
        result_limit: int = 8,
        validator: RetrievalValidator | None = None,
    ) -> None:
        self._hybrid = hybrid
        self._structured = structured
        self._regulatory = regulatory
        self._reranker = reranker
        self._result_limit = result_limit
        self._validator = validator or RetrievalValidator()

    async def search(
        self,
        principal: Principal,
        query: str,
        *,
        route: str = "hybrid_knowledge",
    ) -> list[RetrievalCandidate]:
        candidates = await self._hybrid.search(principal, query, route=route)
        if route in {"hybrid_sql", "hybrid_sql_api"}:
            candidates.extend(
                await self._structured.search(
                    tenant_id=principal.tenant_id,
                    role=principal.role,
                    query=query,
                    limit=self._result_limit,
                )
            )
        if route in {"hybrid_api", "hybrid_sql_api"}:
            candidates.extend(
                await self._regulatory.search(
                    tenant_id=principal.tenant_id,
                    role=principal.role,
                    query=query,
                    limit=self._result_limit,
                )
            )
        unique = list({candidate.chunk_id: candidate for candidate in candidates}.values())
        validated = self._validator.validate(principal, unique)
        reranked = await self._reranker.rerank(query, validated)
        return reranked[: self._result_limit]

