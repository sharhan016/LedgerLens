import re
import uuid
from datetime import UTC

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import ProductMetric
from app.retrieval.domain import RetrievalCandidate
from app.security.principal import Role

METRIC_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"premium savings.*interest rate|interest rate.*premium savings", re.I), "premium_savings_rate"),
    (re.compile(r"gold (credit )?card.*annual fee|annual fee.*gold", re.I), "gold_card_annual_fee"),
    (re.compile(r"configured products|active products", re.I), "active_product_count"),
)


def resolve_metric_keys(query: str) -> tuple[str, ...]:
    return tuple(key for pattern, key in METRIC_PATTERNS if pattern.search(query))


def build_metric_statement(
    *, tenant_id: uuid.UUID, role: Role, metric_keys: tuple[str, ...], limit: int = 10
) -> Select:  # type: ignore[type-arg]
    return (
        select(ProductMetric)
        .where(
            ProductMetric.tenant_id == tenant_id,
            ProductMetric.allowed_roles.overlap([role.value]),
            ProductMetric.metric_key.in_(metric_keys),
        )
        .order_by(ProductMetric.effective_date.desc())
        .limit(limit)
    )


class AllowlistedMetricRetriever:
    """Executes predefined ORM statements; user text is never interpreted as SQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(
        self, *, tenant_id: uuid.UUID, role: Role, query: str, limit: int = 10
    ) -> list[RetrievalCandidate]:
        metric_keys = resolve_metric_keys(query)
        if not metric_keys:
            return []
        metrics = await self._session.scalars(
            build_metric_statement(
                tenant_id=tenant_id,
                role=role,
                metric_keys=metric_keys,
                limit=limit,
            )
        )
        return [
            RetrievalCandidate(
                chunk_id=metric.id,
                document_id=metric.id,
                tenant_id=metric.tenant_id,
                title=metric.label,
                source=metric.source,
                version=metric.effective_date.astimezone(UTC).date().isoformat(),
                content=f"{metric.label}: {metric.value:g} {metric.unit}.",
                section="Structured product metric",
                page_number=None,
                allowed_roles=tuple(metric.allowed_roles),
                keyword_score=1.0,
                rrf_score=1.0 / 61.0,
                retrieval_channel="structured_sql",
            )
            for metric in metrics
        ]

