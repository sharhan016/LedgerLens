import uuid
from typing import Protocol

from app.retrieval.domain import RetrievalCandidate
from app.security.principal import Role


class DenseRetriever(Protocol):
    async def search(
        self,
        *,
        tenant_id: uuid.UUID,
        role: Role,
        embedding: list[float],
        limit: int,
    ) -> list[RetrievalCandidate]: ...


class KeywordRetriever(Protocol):
    async def search(
        self, *, tenant_id: uuid.UUID, role: Role, query: str, limit: int
    ) -> list[RetrievalCandidate]: ...

