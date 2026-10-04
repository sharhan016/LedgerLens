"""Add tenant-scoped allowlisted product metrics.

Revision ID: 0003
Revises: 0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("metric_key", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=240), nullable=False),
        sa.Column("value", sa.Numeric(18, 4), nullable=False),
        sa.Column("unit", sa.String(length=40), nullable=False),
        sa.Column("effective_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("allowed_roles", sa.ARRAY(sa.String(length=32)), nullable=False),
        sa.Column("source", sa.String(length=300), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "metric_key", "effective_date", name="uq_product_metric"
        ),
    )
    op.create_index(
        "ix_product_metrics_tenant_key",
        "product_metrics",
        ["tenant_id", "metric_key"],
    )


def downgrade() -> None:
    op.drop_table("product_metrics")

