import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Document
from app.security.principal import Role


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    source_type: str
    version: str
    status: str
    allowed_roles: tuple[str, ...]


class DocumentRepository(Protocol):
    async def list_visible(self, tenant_id: uuid.UUID, role: Role) -> Sequence[DocumentRecord]: ...

    async def get_visible(
        self, tenant_id: uuid.UUID, role: Role, document_id: uuid.UUID
    ) -> DocumentRecord | None: ...


def build_visible_documents_statement(
    tenant_id: uuid.UUID, role: Role, document_id: uuid.UUID | None = None
) -> Select[tuple[Document]]:
    statement = select(Document).where(
        Document.tenant_id == tenant_id,
        Document.allowed_roles.overlap([role.value]),
    )
    if document_id is not None:
        statement = statement.where(Document.id == document_id)
    return statement.order_by(Document.title, Document.version.desc())


def to_record(document: Document) -> DocumentRecord:
    return DocumentRecord(
        id=document.id,
        tenant_id=document.tenant_id,
        title=document.title,
        source_type=document.source_type,
        version=document.version,
        status=document.status,
        allowed_roles=tuple(document.allowed_roles),
    )


class SqlAlchemyDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_visible(self, tenant_id: uuid.UUID, role: Role) -> Sequence[DocumentRecord]:
        result = await self._session.scalars(build_visible_documents_statement(tenant_id, role))
        return [to_record(document) for document in result]

    async def get_visible(
        self, tenant_id: uuid.UUID, role: Role, document_id: uuid.UUID
    ) -> DocumentRecord | None:
        result = await self._session.scalar(
            build_visible_documents_statement(tenant_id, role, document_id)
        )
        return to_record(result) if result is not None else None


class InMemoryDocumentRepository:
    def __init__(self, records: Sequence[DocumentRecord]) -> None:
        self._records = tuple(records)

    async def list_visible(self, tenant_id: uuid.UUID, role: Role) -> Sequence[DocumentRecord]:
        return tuple(
            record
            for record in self._records
            if record.tenant_id == tenant_id and role.value in record.allowed_roles
        )

    async def get_visible(
        self, tenant_id: uuid.UUID, role: Role, document_id: uuid.UUID
    ) -> DocumentRecord | None:
        return next(
            (
                record
                for record in await self.list_visible(tenant_id, role)
                if record.id == document_id
            ),
            None,
        )

