import uuid

from pydantic import BaseModel

from app.security.principal import Role


class PrincipalResponse(BaseModel):
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: Role


class DemoLoginRequest(BaseModel):
    persona: Role


class DemoLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: PrincipalResponse
    display_name: str
    tenant_name: str
    demo_auth: bool = True
