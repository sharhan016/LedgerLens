import uuid
from typing import Protocol

from app.generation.domain import LLMGeneration
from app.security.principal import Principal, Role


class KnowledgeVersionProvider(Protocol):
    async def get(self, tenant_id: uuid.UUID) -> str: ...


class GenerationCache(Protocol):
    async def get(
        self,
        *,
        tenant_id: uuid.UUID,
        role: Role,
        query_embedding: list[float],
        knowledge_version: str,
        context_fingerprint: str,
    ) -> LLMGeneration | None: ...

    async def put(
        self,
        *,
        tenant_id: uuid.UUID,
        role: Role,
        query: str,
        query_embedding: list[float],
        knowledge_version: str,
        context_fingerprint: str,
        generation: LLMGeneration,
    ) -> None: ...


class ConversationRecorder(Protocol):
    async def record_exchange(
        self,
        *,
        principal: Principal,
        conversation_id: uuid.UUID | None,
        question: str,
        answer: str,
        metadata: dict[str, object],
    ) -> uuid.UUID: ...


class AuditSink(Protocol):
    async def record(
        self,
        *,
        principal: Principal,
        action: str,
        resource_type: str,
        resource_id: str | None,
        details: dict[str, object],
    ) -> None: ...

