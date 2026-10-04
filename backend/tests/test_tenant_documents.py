import uuid

import pytest
from sqlalchemy.dialects import postgresql

from app.repositories.documents import (
    DocumentRecord,
    InMemoryDocumentRepository,
    build_visible_documents_statement,
)
from app.security.principal import Principal, Role
from app.services.documents import DocumentService


def record(tenant_id: uuid.UUID, title: str, *roles: Role) -> DocumentRecord:
    return DocumentRecord(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        title=title,
        source_type="policy",
        version="2026.1",
        status="ready",
        allowed_roles=tuple(role.value for role in roles),
    )


@pytest.mark.asyncio
async def test_cross_tenant_and_role_records_never_leave_repository_boundary() -> None:
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    visible = record(tenant_a, "Savings policy", Role.ANALYST)
    wrong_tenant = record(tenant_b, "Other bank policy", Role.ANALYST)
    wrong_role = record(tenant_a, "Compliance manual", Role.COMPLIANCE)
    service = DocumentService(InMemoryDocumentRepository([visible, wrong_tenant, wrong_role]))
    principal = Principal(uuid.uuid4(), tenant_a, Role.ANALYST)

    documents = await service.list_documents(principal)

    assert documents == (visible,)
    assert await service.get_document(principal, wrong_tenant.id) is None
    assert await service.get_document(principal, wrong_role.id) is None


def test_sql_repository_statement_always_contains_tenant_and_role_predicates() -> None:
    statement = build_visible_documents_statement(uuid.uuid4(), Role.ANALYST)
    sql = str(statement.compile(dialect=postgresql.dialect()))

    assert "documents.tenant_id" in sql
    assert "documents.allowed_roles" in sql
    assert "&&" in sql

