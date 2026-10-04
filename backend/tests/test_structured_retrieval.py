import uuid

from sqlalchemy.dialects import postgresql

from app.retrieval.structured import build_metric_statement, resolve_metric_keys
from app.security.principal import Role


def test_metric_catalog_maps_known_questions_without_accepting_sql() -> None:
    assert resolve_metric_keys("What is the Premium Savings interest rate?") == (
        "premium_savings_rate",
    )
    assert resolve_metric_keys("'; DROP TABLE product_metrics; --") == ()
    assert resolve_metric_keys("select * from users") == ()


def test_metric_statement_is_tenant_role_and_key_scoped() -> None:
    statement = build_metric_statement(
        tenant_id=uuid.uuid4(),
        role=Role.ANALYST,
        metric_keys=("premium_savings_rate",),
    )
    sql = str(statement.compile(dialect=postgresql.dialect()))

    assert "product_metrics.tenant_id" in sql
    assert "product_metrics.allowed_roles" in sql and "&&" in sql
    assert "product_metrics.metric_key IN" in sql
    assert "effective_date DESC" in sql

