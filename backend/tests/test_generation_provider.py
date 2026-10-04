import json

import httpx
import pytest

from app.generation.domain import ContextSource, GenerationRequest
from app.generation.providers import DemoExtractiveProvider, OpenAICompatibleProvider


@pytest.mark.asyncio
async def test_openai_compatible_provider_sends_bounded_context_and_parses_json() -> None:
    captured: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["authorization"] = request.headers.get("Authorization")
        captured["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "answer": "The minimum balance is INR 25,000 [S1].",
                                    "citations": ["S1"],
                                }
                            )
                        }
                    }
                ]
            },
        )

    source = ContextSource(
        "S1",
        "chunk",
        "document",
        "Policy",
        "policy.md",
        "1",
        "Minimum balance INR 25,000.",
        "Balance",
        None,
    )
    provider = OpenAICompatibleProvider(
        base_url="https://provider.example/v1",
        model="banking-model",
        api_key="secret",
        transport=httpx.MockTransport(handler),
    )

    result = await provider.generate(
        GenerationRequest("What is the balance?", "[S1] Minimum balance INR 25,000.", (source,), "fact")
    )

    assert result.answer.endswith("[S1].")
    assert result.cited_source_ids == ("S1",)
    assert captured["authorization"] == "Bearer secret"
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["temperature"] == 0
    assert "[S1] Minimum balance" in payload["messages"][1]["content"]


@pytest.mark.asyncio
async def test_demo_extractive_provider_is_explicitly_labeled_and_cited() -> None:
    source = ContextSource(
        "S1",
        "chunk",
        "document",
        "Policy",
        "policy.md",
        "1",
        "The account requires an average monthly balance of INR 25,000.",
        "Balance",
        None,
    )

    result = await DemoExtractiveProvider().generate(
        GenerationRequest("What is the minimum balance?", source.content, (source,), "fact")
    )

    assert result.model == "demo-extractive-not-llm"
    assert "INR 25,000" in result.answer
    assert result.answer.endswith("[S1].")
    assert result.cited_source_ids == ("S1",)
