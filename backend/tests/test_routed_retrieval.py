import uuid

import pytest

from app.reranking.deterministic import TokenOverlapReranker
from app.retrieval.domain import RetrievalCandidate
from app.retrieval.routed import RetrievalValidator, RoutedRetrievalOrchestrator
from app.security.principal import Principal, Role


def item(
    tenant_id: uuid.UUID,
    *,
    channel: str,
    content: str,
    roles: tuple[str, ...] = ("analyst",),
) -> RetrievalCandidate:
    return RetrievalCandidate(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        tenant_id=tenant_id,
        title=channel,
        source=f"{channel}.example",
        version="1",
        content=content,
        section=None,
        page_number=None,
        allowed_roles=roles,
        retrieval_channel=channel,
    )


class HybridStub:
    def __init__(self, results):  # type: ignore[no-untyped-def]
        self.results = results

    async def search(self, principal, query, *, route="hybrid_knowledge"):  # type: ignore[no-untyped-def]
        return list(self.results)


class SupplementalStub:
    def __init__(self, results):  # type: ignore[no-untyped-def]
        self.results = results
        self.calls = 0

    async def search(self, *, tenant_id, role, query, limit):  # type: ignore[no-untyped-def]
        self.calls += 1
        return list(self.results)


@pytest.mark.asyncio
async def test_routed_orchestrator_combines_selected_sources_and_validates_all_results() -> None:
    tenant_id = uuid.uuid4()
    principal = Principal(uuid.uuid4(), tenant_id, Role.ANALYST)
    hybrid = item(tenant_id, channel="hybrid", content="premium interest rate policy")
    structured = item(
        tenant_id,
        channel="structured_sql",
        content="premium savings interest rate 4.10 percent",
    )
    malicious = item(
        uuid.uuid4(),
        channel="regulatory_api:live",
        content="cross tenant content",
    )
    sql = SupplementalStub([structured])
    api = SupplementalStub([malicious])
    orchestrator = RoutedRetrievalOrchestrator(
        hybrid=HybridStub([hybrid]),
        structured=sql,
        regulatory=api,
        reranker=TokenOverlapReranker(),
    )

    results = await orchestrator.search(
        principal,
        "premium savings interest rate regulatory bulletin",
        route="hybrid_sql_api",
    )

    assert {result.retrieval_channel for result in results} == {"hybrid", "structured_sql"}
    assert all(result.tenant_id == tenant_id for result in results)
    assert sql.calls == 1 and api.calls == 1


def test_validator_fails_closed_for_role_empty_content_and_missing_source() -> None:
    tenant_id = uuid.uuid4()
    principal = Principal(uuid.uuid4(), tenant_id, Role.ANALYST)
    allowed = item(tenant_id, channel="hybrid", content="valid")
    wrong_role = item(
        tenant_id,
        channel="hybrid",
        content="restricted",
        roles=("compliance",),
    )
    empty = item(tenant_id, channel="hybrid", content=" ")

    assert RetrievalValidator().validate(principal, [allowed, wrong_role, empty]) == [allowed]

