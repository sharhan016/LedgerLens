import hashlib
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.generation.domain import LLMGeneration
from app.models.entities import (
    AuditEvent,
    Conversation,
    ConversationMessage,
    Document,
    SemanticCacheEntry,
)
from app.security.principal import Principal, Role


class PostgresKnowledgeVersionProvider:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, tenant_id: uuid.UUID) -> str:
        count, latest = (
            await self._session.execute(
                select(func.count(Document.id), func.max(Document.updated_at)).where(
                    Document.tenant_id == tenant_id,
                    Document.status == "ready",
                )
            )
        ).one()
        value = f"{count}:{latest.isoformat() if latest else 'empty'}"
        return hashlib.sha256(value.encode()).hexdigest()


class PostgresGenerationCache:
    def __init__(
        self,
        session: AsyncSession,
        *,
        similarity_threshold: float = 0.92,
        ttl_minutes: int = 60,
    ) -> None:
        self._session = session
        self._max_distance = 1.0 - similarity_threshold
        self._ttl = timedelta(minutes=ttl_minutes)

    async def get(
        self,
        *,
        tenant_id: uuid.UUID,
        role: Role,
        query_embedding: list[float],
        knowledge_version: str,
        context_fingerprint: str,
    ) -> LLMGeneration | None:
        distance = SemanticCacheEntry.query_embedding.cosine_distance(query_embedding)
        entry = await self._session.scalar(
            select(SemanticCacheEntry)
            .where(
                SemanticCacheEntry.tenant_id == tenant_id,
                SemanticCacheEntry.role == role.value,
                SemanticCacheEntry.knowledge_version == knowledge_version,
                SemanticCacheEntry.context_fingerprint == context_fingerprint,
                SemanticCacheEntry.expires_at > func.now(),
                distance <= self._max_distance,
            )
            .order_by(distance)
            .limit(1)
        )
        if entry is None:
            return None
        return LLMGeneration(
            answer=str(entry.generation["answer"]),
            cited_source_ids=tuple(entry.generation.get("cited_source_ids", [])),
            model=str(entry.generation["model"]),
        )

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
        self._session.add(
            SemanticCacheEntry(
                tenant_id=tenant_id,
                role=role.value,
                query_hash=hashlib.sha256(query.encode()).hexdigest(),
                query_embedding=query_embedding,
                knowledge_version=knowledge_version,
                context_fingerprint=context_fingerprint,
                generation={
                    "answer": generation.answer,
                    "cited_source_ids": list(generation.cited_source_ids),
                    "model": generation.model,
                },
                expires_at=datetime.now(UTC) + self._ttl,
            )
        )
        await self._session.commit()


class PostgresConversationRecorder:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_exchange(
        self,
        *,
        principal: Principal,
        conversation_id: uuid.UUID | None,
        question: str,
        answer: str,
        metadata: dict[str, object],
    ) -> uuid.UUID:
        conversation = None
        if conversation_id is not None:
            conversation = await self._session.scalar(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.tenant_id == principal.tenant_id,
                    Conversation.user_id == principal.user_id,
                )
            )
            if conversation is None:
                raise ValueError("conversation not found")
        else:
            conversation = Conversation(
                tenant_id=principal.tenant_id,
                user_id=principal.user_id,
                title=question[:237] + ("..." if len(question) > 237 else ""),
            )
            self._session.add(conversation)
            await self._session.flush()
        self._session.add_all(
            [
                ConversationMessage(
                    tenant_id=principal.tenant_id,
                    conversation_id=conversation.id,
                    role="user",
                    content=question,
                    message_metadata={},
                ),
                ConversationMessage(
                    tenant_id=principal.tenant_id,
                    conversation_id=conversation.id,
                    role="assistant",
                    content=answer,
                    message_metadata=metadata,
                ),
            ]
        )
        conversation.updated_at = datetime.now(UTC)
        await self._session.commit()
        return conversation.id


class PostgresAuditSink:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        principal: Principal,
        action: str,
        resource_type: str,
        resource_id: str | None,
        details: dict[str, object],
    ) -> None:
        self._session.add(
            AuditEvent(
                tenant_id=principal.tenant_id,
                actor_id=principal.user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
            )
        )
        await self._session.commit()

