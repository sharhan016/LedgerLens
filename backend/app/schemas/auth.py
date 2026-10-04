import uuid

from pydantic import BaseModel

from app.security.principal import Role


class PrincipalResponse(BaseModel):
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: Role

