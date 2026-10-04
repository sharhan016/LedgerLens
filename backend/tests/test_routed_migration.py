from pathlib import Path


def test_product_metrics_migration_is_tenant_scoped() -> None:
    migration = (
        Path(__file__).parents[1] / "migrations/versions/0003_product_metrics.py"
    ).read_text(encoding="utf-8")

    assert '"product_metrics"' in migration
    assert 'sa.Column("tenant_id"' in migration
    assert 'sa.Column("allowed_roles"' in migration
    assert "uq_product_metric" in migration

