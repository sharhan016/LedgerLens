from pathlib import Path


def test_retrieval_migration_adds_generated_fts_and_hnsw_indexes() -> None:
    migration = (
        Path(__file__).parents[1] / "migrations/versions/0002_hybrid_retrieval_indexes.py"
    ).read_text(encoding="utf-8")

    assert "to_tsvector('english', content)" in migration
    assert "USING gin (search_vector)" in migration
    assert "USING hnsw (embedding vector_cosine_ops)" in migration

