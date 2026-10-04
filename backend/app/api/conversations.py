import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entities import Conversation, ConversationMessage
from app.schemas.conversations import (
    ConversationDetailResponse,
    ConversationMessageResponse,
    ConversationSummaryResponse,
)
from app.security.dependencies import get_current_principal
from app.security.principal import Principal

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])

PrincipalDependency = Annotated[Principal, Depends(get_current_principal)]
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=list[ConversationSummaryResponse])
async def list_conversations(
    principal: PrincipalDependency,
    session: SessionDependency,
) -> list[ConversationSummaryResponse]:
    conversations = await session.scalars(
        select(Conversation)
        .where(
            Conversation.tenant_id == principal.tenant_id,
            Conversation.user_id == principal.user_id,
        )
        .order_by(Conversation.updated_at.desc())
        .limit(50)
    )
    return [
        ConversationSummaryResponse(
            id=item.id,
            title=item.title,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in conversations
    ]


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    principal: PrincipalDependency,
    session: SessionDependency,
) -> ConversationDetailResponse:
    conversation = await session.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == principal.tenant_id,
            Conversation.user_id == principal.user_id,
        )
    )
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    messages = await session.scalars(
        select(ConversationMessage)
        .where(
            ConversationMessage.tenant_id == principal.tenant_id,
            ConversationMessage.conversation_id == conversation.id,
        )
        .order_by(ConversationMessage.created_at)
    )
    return ConversationDetailResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[
            ConversationMessageResponse(
                id=message.id,
                role=message.role,
                content=message.content,
                metadata=message.message_metadata,
                created_at=message.created_at,
            )
            for message in messages
        ],
    )

