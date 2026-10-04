import uuid
from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Chunk, Document
from app.retrieval.domain import RetrievalCandidate
from app.security.principal import Role


def _base_columns():  # type: ignore[no-untyped-def]
    return (
        Chunk.id.label("chunk_id"),
        Document.id.label("document_id"),
        Chunk.tenant_id,
        Document.title,
        Document.source_key.label("source"),
        Document.version,
        Chunk.content,
        Chunk.section,
        Chunk.page_number,
        Document.allowed_roles,
    )


def build_dense_statement(
    *, tenant_id: uuid.UUID, role: Role, embedding: list[float], limit: int
) -> Select:  # type: ignore[type-arg]
    distance = Chunk.embedding.cosine_distance(embedding)
    return (
        select(*_base_columns(), (1.0 - distance).label("score"))
        .join(Document, Document.id == Chunk.document_id)
        .where(
            Chunk.tenant_id == tenant_id,
            Document.tenant_id == tenant_id,
            Document.allowed_roles.overlap([role.value]),
            Chunk.embedding.is_not(None),
        )
        .order_by(distance)
        .limit(limit)
    )


def build_keyword_statement(
    *, tenant_id: uuid.UUID, role: Role, query: str, limit: int
) -> Select:  # type: ignore[type-arg]
    parsed_query = func.websearch_to_tsquery("english", query)
    rank = func.ts_rank_cd(Chunk.search_vector, parsed_query)
    return (
        select(*_base_columns(), rank.label("score"))
        .join(Document, Document.id == Chunk.document_id)
        .where(
            Chunk.tenant_id == tenant_id,
            Document.tenant_id == tenant_id,
            Document.allowed_roles.overlap([role.value]),
            Chunk.search_vector.op("@@")(parsed_query),
        )
        .order_by(rank.desc())
        .limit(limit)
    )


def _rows_to_candidates(rows: Sequence, channel: str) -> list[RetrievalCandidate]:  # type: ignore[type-arg]
    candidates = []
    for row in rows:
        candidate = RetrievalCandidate(
            chunk_id=row.chunk_id,
            document_id=row.document_id,
            tenant_id=row.tenant_id,
            title=row.title,
            source=row.source,
            version=row.version,
            content=row.content,
            section=row.section,
            page_number=row.page_number,
            allowed_roles=tuple(row.allowed_roles),
            dense_score=float(row.score) if channel == "dense" else None,
            keyword_score=float(row.score) if channel == "keyword" else None,
        )
        candidates.append(candidate)
    return candidates


class PostgresDenseRetriever:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(
        self,
        *,
        tenant_id: uuid.UUID,
        role: Role,
        embedding: list[float],
        limit: int,
    ) -> list[RetrievalCandidate]:
        rows = (await self._session.execute(
            build_dense_statement(
                tenant_id=tenant_id, role=role, embedding=embedding, limit=limit
            )
        )).all()
        return _rows_to_candidates(rows, "dense")


class PostgresKeywordRetriever:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(
        self, *, tenant_id: uuid.UUID, role: Role, query: str, limit: int
    ) -> list[RetrievalCandidate]:
        rows = (await self._session.execute(
            build_keyword_statement(tenant_id=tenant_id, role=role, query=query, limit=limit)
        )).all()
        return _rows_to_candidates(rows, "keyword")

