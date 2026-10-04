import json
import re
from typing import Protocol

import httpx

from app.generation.domain import GenerationRequest, LLMGeneration

CITATION_PATTERN = re.compile(r"\[(S\d+)\]")


class LLMProvider(Protocol):
    async def generate(self, request: GenerationRequest) -> LLMGeneration: ...


class GenerationProviderError(RuntimeError):
    pass


class DemoExtractiveProvider:
    """Offline demo fallback; deliberately labeled as non-LLM generation."""

    cache_namespace = "demo-extractive-v2"

    _stopwords = {
        "a", "an", "and", "are", "can", "for", "is", "of", "on", "the", "to", "what",
        "when", "which", "with",
    }

    async def generate(self, request: GenerationRequest) -> LLMGeneration:
        query_terms = {
            token for token in re.findall(r"[a-z0-9]+", request.question.lower())
            if token not in self._stopwords
        }
        ranked: list[tuple[int, int, str, str]] = []
        for source_index, source in enumerate(request.sources):
            sentences = re.split(r"(?<=[.!?])\s+|\n+", source.content)
            for sentence in sentences:
                clean = " ".join(sentence.split()).strip(" #-\t")
                if len(clean) < 24:
                    continue
                terms = set(re.findall(r"[a-z0-9]+", clean.lower()))
                ranked.append((-source_index, len(query_terms & terms), clean, source.source_id))
        ranked.sort(reverse=True)
        if not ranked:
            raise GenerationProviderError("demo extractive provider received no usable evidence")
        best = ranked[0]
        answer = f"{best[2].rstrip('.')} [{best[3]}]."
        return LLMGeneration(answer, (best[3],), "demo-extractive-not-llm")


def parse_generation_content(content: str, model: str) -> LLMGeneration:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        answer = content.strip()
        citations = tuple(dict.fromkeys(CITATION_PATTERN.findall(answer)))
        if not answer:
            raise GenerationProviderError("LLM returned an empty response") from None
        return LLMGeneration(answer=answer, cited_source_ids=citations, model=model)

    answer = str(payload.get("answer", "")).strip()
    if not answer:
        raise GenerationProviderError("LLM response JSON did not contain an answer")
    declared = payload.get("citations", [])
    citations = tuple(
        dict.fromkeys(
            [str(item) for item in declared if re.fullmatch(r"S\d+", str(item))]
            + CITATION_PATTERN.findall(answer)
        )
    )
    return LLMGeneration(answer=answer, cited_source_ids=citations, model=model)


class OpenAICompatibleProvider:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str | None,
        timeout_seconds: float = 45.0,
        extra_headers: dict[str, str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key = api_key
        self._timeout = timeout_seconds
        self._headers = extra_headers or {}
        self._transport = transport
        self.cache_namespace = f"openai-compatible:{self._base_url}:{self._model}"

    async def generate(self, request: GenerationRequest) -> LLMGeneration:
        headers = {"Content-Type": "application/json", **self._headers}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        payload = {
            "model": self._model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are LedgerLens, a banking policy assistant. Answer only from the "
                        "provided labeled sources. Every factual sentence must include one or "
                        "more source markers such as [S1]. If evidence is insufficient, say so. "
                        "Return JSON with keys answer and citations; citations is an array of "
                        "source IDs used in the answer."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Intent: {request.intent}\nQuestion: {request.question}\n\n"
                        f"Authorized sources:\n{request.context}"
                    ),
                },
            ],
        }
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise GenerationProviderError("LLM provider request failed") from error
        try:
            content = response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise GenerationProviderError("LLM provider returned an invalid response") from error
        return parse_generation_content(str(content), self._model)


class DeterministicGroundedProvider:
    """Deterministic test double that emits only an explicitly supplied answer."""

    def __init__(self, answer: str, *, model: str = "deterministic-test-provider") -> None:
        self.answer = answer
        self.model = model
        self.cache_namespace = f"deterministic:{model}"
        self.requests: list[GenerationRequest] = []

    async def generate(self, request: GenerationRequest) -> LLMGeneration:
        self.requests.append(request)
        citations = tuple(dict.fromkeys(CITATION_PATTERN.findall(self.answer)))
        return LLMGeneration(self.answer, citations, self.model)
