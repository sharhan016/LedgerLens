from pathlib import Path

import httpx
import pytest

from app.retrieval.api_sources import FixtureRegulatoryAdapter, HttpRegulatoryAdapter


@pytest.mark.asyncio
async def test_fixture_adapter_is_explicitly_mock_and_returns_typed_bulletins() -> None:
    path = Path(__file__).parents[2] / "data/sample/api/regulatory-bulletins.json"
    adapter = FixtureRegulatoryAdapter(path)

    results = await adapter.search("KYC remediation", limit=2)

    assert adapter.integration_mode == "mock-demo"
    assert len(results) == 2
    assert results[0].id == "SRB-2026-014"
    assert results[0].source_url.startswith("https://regulator.invalid/")


@pytest.mark.asyncio
async def test_live_adapter_uses_typed_contract_query_params_and_https() -> None:
    captured: dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["query"] = str(request.url.params.get("q"))
        captured["limit"] = str(request.url.params.get("limit"))
        return httpx.Response(
            200,
            json={
                "bulletins": [
                    {
                        "id": "LIVE-1",
                        "title": "Guidance",
                        "published_at": "2026-01-01",
                        "summary": "Typed response.",
                        "source_url": "https://regulator.example/guidance/1",
                    }
                ]
            },
        )

    adapter = HttpRegulatoryAdapter(
        "https://regulator.example/v1",
        timeout_seconds=0.5,
        transport=httpx.MockTransport(handler),
    )
    results = await adapter.search("fraud evidence", limit=3)

    assert results[0].id == "LIVE-1"
    assert captured == {"query": "fraud evidence", "limit": "3"}
    with pytest.raises(ValueError, match="HTTPS"):
        HttpRegulatoryAdapter("http://regulator.example/v1")

