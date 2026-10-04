import asyncio
import re
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import SessionFactory, engine
from app.demo import DEMO_TENANT_ID, DEMO_TENANT_NAME, DEMO_USERS
from app.embeddings.dependencies import get_embedding_provider
from app.ingestion.domain import IngestionMetadata, IngestionSource
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.repository import SqlAlchemyIngestionRepository
from app.models.entities import Document, ProductMetric, Tenant, User
from app.security.principal import Role


def _frontmatter(content: str) -> dict[str, str]:
    if not content.startswith("---"):
        return {}
    _, raw, _body = content.split("---", 2)
    values: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


async def seed_demo() -> None:
    settings = get_settings()
    corpus = Path(settings.demo_data_path)
    if not corpus.is_dir():
        raise RuntimeError(f"synthetic demo corpus not found: {corpus}")

    async with SessionFactory() as session:
        tenant = await session.get(Tenant, DEMO_TENANT_ID)
        if tenant is None:
            session.add(
                Tenant(
                    id=DEMO_TENANT_ID,
                    slug="northstar-union-bank-demo",
                    name=DEMO_TENANT_NAME,
                    is_active=True,
                )
            )
        for role, (user_id, email, display_name) in DEMO_USERS.items():
            if await session.get(User, user_id) is None:
                session.add(
                    User(
                        id=user_id,
                        tenant_id=DEMO_TENANT_ID,
                        email=email,
                        display_name=display_name,
                        role=role.value,
                        is_active=True,
                    )
                )
        await session.commit()

        pipeline = IngestionPipeline(
            SqlAlchemyIngestionRepository(session),
            embedding_provider=get_embedding_provider(),
        )
        for path in sorted(corpus.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            values = _frontmatter(content)
            version = values.get("version", "demo")
            exists = await session.scalar(
                select(Document.id).where(
                    Document.tenant_id == DEMO_TENANT_ID,
                    Document.source_key == path.name,
                    Document.version == version,
                )
            )
            if exists is not None:
                continue
            roles = tuple(
                Role(value.strip())
                for value in values.get("allowed_roles", "analyst,compliance,admin").split(",")
                if value.strip() in {role.value for role in Role}
            )
            effective = values.get("effective_date")
            await pipeline.ingest(
                tenant_id=DEMO_TENANT_ID,
                source=IngestionSource(path.name, content.encode()),
                metadata=IngestionMetadata(
                    title=values.get("title", re.sub(r"[-_]", " ", path.stem).title()),
                    version=version,
                    source_type="policy",
                    classification=values.get("classification", "internal"),
                    product=values.get("product"),
                    effective_date=date.fromisoformat(effective) if effective else None,
                    allowed_roles=roles,
                ),
            )

        metrics = (
            ("premium_savings_minimum_balance", "Premium Savings minimum balance", 25000, "INR"),
            ("personal_loan_processing_fee", "Personal loan processing fee", 1.25, "percent"),
            ("gold_card_income_threshold", "Gold Card annual income threshold", 900000, "INR"),
        )
        for key, label, value, unit in metrics:
            found = await session.scalar(
                select(ProductMetric.id).where(
                    ProductMetric.tenant_id == DEMO_TENANT_ID,
                    ProductMetric.metric_key == key,
                )
            )
            if found is None:
                session.add(
                    ProductMetric(
                        tenant_id=DEMO_TENANT_ID,
                        metric_key=key,
                        label=label,
                        value=value,
                        unit=unit,
                        effective_date=datetime(2026, 7, 1, tzinfo=UTC),
                        allowed_roles=[role.value for role in (Role.ANALYST, Role.COMPLIANCE, Role.ADMIN)],
                        source="Northstar synthetic product ledger",
                    )
                )
        await session.commit()
    await engine.dispose()
    print("Synthetic LedgerLens demo data is ready.")


if __name__ == "__main__":
    asyncio.run(seed_demo())
