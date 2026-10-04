import uuid

from sqlalchemy.dialects import postgresql

from app.retrieval.postgres import build_dense_statement, build_keyword_statement
from app.security.principal import Role


def compile_sql(statement) -> str:  # type: ignore[no-untyped-def]
    return str(statement.compile(dialect=postgresql.dialect()))


def test_dense_query_filters_tenant_role_and_null_vectors_before_ranking() -> None:
    sql = compile_sql(
        build_dense_statement(
            tenant_id=uuid.uuid4(),
            role=Role.ANALYST,
            embedding=[0.0] * 384,
            limit=30,
        )
    )

    assert sql.count("tenant_id") >= 2
    assert "allowed_roles" in sql and "&&" in sql
    assert "embedding IS NOT NULL" in sql
    assert "<=>" in sql


def test_keyword_query_filters_tenant_role_and_uses_websearch_rank() -> None:
    sql = compile_sql(
        build_keyword_statement(
            tenant_id=uuid.uuid4(),
            role=Role.COMPLIANCE,
            query="failed KYC verification",
            limit=30,
        )
    )

    assert sql.count("tenant_id") >= 2
    assert "allowed_roles" in sql and "&&" in sql
    assert "websearch_to_tsquery" in sql
    assert "ts_rank_cd" in sql
    assert "@@" in sql

