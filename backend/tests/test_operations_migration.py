from pathlib import Path


def test_operations_migration_scopes_conversations_and_cache_by_tenant() -> None:
    migration = (
        Path(__file__).parents[1]
        / "migrations/versions/0004_conversations_and_semantic_cache.py"
    ).read_text(encoding="utf-8")

    for table in ("conversations", "conversation_messages", "semantic_cache_entries"):
        assert f'"{table}"' in migration
    assert migration.count('sa.Column("tenant_id"') >= 3
    assert 'sa.Column("role"' in migration
    assert 'sa.Column("knowledge_version"' in migration
    assert 'sa.Column("context_fingerprint"' in migration
    assert "query_embedding vector_cosine_ops" in migration

