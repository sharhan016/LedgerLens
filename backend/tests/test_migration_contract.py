from pathlib import Path


def test_initial_migration_installs_vector_and_tenant_scoped_foundations() -> None:
    migration = (
        Path(__file__).parents[1] / "migrations/versions/0001_tenant_security_foundation.py"
    ).read_text(encoding="utf-8")

    assert "CREATE EXTENSION IF NOT EXISTS vector" in migration
    for table in ("tenants", "users", "documents", "chunks", "audit_events"):
        assert f'"{table}"' in migration
    assert migration.count('sa.Column("tenant_id"') >= 4
    assert "pgvector.sqlalchemy.Vector" in migration

