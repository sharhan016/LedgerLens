import uuid

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    source_type: str
    version: str
    status: str

