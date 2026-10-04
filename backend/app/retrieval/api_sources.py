import json
import re
import uuid
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.retrieval.domain import RetrievalCandidate
from app.security.principal import Role


@dataclass(frozen=True, slots=True)
class RegulatoryBulletin:
    id: str
    title: str
    published_at: date
    summary: str
    source_url: str


class RegulatorySourceError(RuntimeError):
    pass


def parse_bulletin(item: object) -> RegulatoryBulletin:
    if not isinstance(item, dict):
        raise RegulatorySourceError("regulatory source item must be an object")
    try:
        return RegulatoryBulletin(
            id=str(item["id"]),
            title=str(item["title"]),
            published_at=date.fromisoformat(str(item["published_at"])),
            summary=str(item["summary"]),
            source_url=str(item["source_url"]),
        )
    except (KeyError, ValueError, TypeError) as error:
        raise RegulatorySourceError("regulatory source item has an invalid schema") from error


class FixtureRegulatoryAdapter:
    """Explicit demo adapter backed by a checked-in synthetic response fixture."""

    integration_mode = "mock-demo"

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    async def search(self, query: str, *, limit: int = 5) -> list[RegulatoryBulletin]:
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        if payload.get("synthetic") is not True:
            raise RegulatorySourceError("fixture must be explicitly marked synthetic")
        query_tokens = set(re.findall(r"\w+", query.lower()))
        bulletins = [parse_bulletin(item) for item in payload.get("bulletins", [])]
        ranked = sorted(
            bulletins,
            key=lambda item: len(
                query_tokens & set(re.findall(r"\w+", f"{item.title} {item.summary}".lower()))
            ),
            reverse=True,
        )
        return ranked[:limit]


class HttpRegulatoryAdapter:
    integration_mode = "live"

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        parsed = urlparse(base_url)
        if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1"}:
            raise ValueError("live regulatory API URL must use HTTPS")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._transport = transport

    async def search(self, query: str, *, limit: int = 5) -> list[RegulatoryBulletin]:
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.get(
                    f"{self._base_url}/bulletins",
                    params={"q": query, "limit": limit},
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, json.JSONDecodeError) as error:
            raise RegulatorySourceError("regulatory API request failed") from error
        if not isinstance(payload, dict):
            raise RegulatorySourceError("regulatory API response must be an object")
        return [parse_bulletin(item) for item in payload.get("bulletins", [])][:limit]


class RegulatoryRetriever:
    def __init__(self, adapter: FixtureRegulatoryAdapter | HttpRegulatoryAdapter) -> None:
        self._adapter = adapter

    async def search(
        self, *, tenant_id: uuid.UUID, role: Role, query: str, limit: int = 5
    ) -> list[RetrievalCandidate]:
        bulletins = await self._adapter.search(query, limit=limit)
        allowed_roles = tuple(member.value for member in Role)
        return [
            RetrievalCandidate(
                chunk_id=uuid.uuid5(uuid.NAMESPACE_URL, bulletin.source_url),
                document_id=uuid.uuid5(uuid.NAMESPACE_URL, f"document:{bulletin.source_url}"),
                tenant_id=tenant_id,
                title=bulletin.title,
                source=bulletin.source_url,
                version=bulletin.published_at.isoformat(),
                content=bulletin.summary,
                section="Regulatory bulletin",
                page_number=None,
                allowed_roles=allowed_roles,
                keyword_score=1.0,
                rrf_score=1.0 / 61.0,
                retrieval_channel=f"regulatory_api:{self._adapter.integration_mode}",
            )
            for bulletin in bulletins
            if role.value in allowed_roles
        ]

