import uuid
from datetime import datetime

from pydantic import BaseModel


class ConversationSummaryResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    metadata: dict[str, object]
    created_at: datetime


class ConversationDetailResponse(ConversationSummaryResponse):
    messages: list[ConversationMessageResponse]

