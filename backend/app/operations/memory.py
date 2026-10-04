import math
import uuid
from dataclasses import dataclass

from app.generation.domain import LLMGeneration
from app.security.principal import Principal, Role


@dataclass(slots=True)
class CacheRecord:
    tenant_id: uuid.UUID
    role: Role
    embedding: list[float]
    knowledge_version: str
    context_fingerprint: str
    generation: LLMGeneration


class InMemoryGenerationCache:
    def __init__(self, similarity_threshold: float = 0.92) -> None:
        self._threshold = similarity_threshold
        self.records: list[CacheRecord] = []

    @staticmethod
    def _similarity(left: list[float], right: list[float]) -> float:
        dot = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = math.sqrt(sum(value * value for value in left)) or 1.0
        right_norm = math.sqrt(sum(value * value for value in right)) or 1.0
        return dot / (left_norm * right_norm)

    async def get(
        self,
        *,
        tenant_id: uuid.UUID,
        role: Role,
        query_embedding: list[float],
        knowledge_version: str,
        context_fingerprint: str,
    ) -> LLMGeneration | None:
        matches = [
            record
            for record in self.records
            if record.tenant_id == tenant_id
            and record.role == role
            and record.knowledge_version == knowledge_version
            and record.context_fingerprint == context_fingerprint
            and self._similarity(record.embedding, query_embedding) >= self._threshold
        ]
        return matches[0].generation if matches else None

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
    ) -> None:
        self.records.append(
            CacheRecord(
                tenant_id,
                role,
                query_embedding,
                knowledge_version,
                context_fingerprint,
                generation,
            )
        )


class StaticKnowledgeVersion:
    def __init__(self, value: str = "v1") -> None:
        self.value = value

    async def get(self, tenant_id: uuid.UUID) -> str:
        return self.value


class InMemoryConversationRecorder:
    def __init__(self) -> None:
        self.exchanges: list[dict[str, object]] = []

    async def record_exchange(
        self,
        *,
        principal: Principal,
        conversation_id: uuid.UUID | None,
        question: str,
        answer: str,
        metadata: dict[str, object],
    ) -> uuid.UUID:
        resolved = conversation_id or uuid.uuid4()
        self.exchanges.append(
            {
                "principal": principal,
                "conversation_id": resolved,
                "question": question,
                "answer": answer,
                "metadata": metadata,
            }
        )
        return resolved


class InMemoryAuditSink:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    async def record(self, **event: object) -> None:
        self.events.append(event)

