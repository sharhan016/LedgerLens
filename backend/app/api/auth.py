from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.auth import PrincipalResponse
from app.security.dependencies import get_current_principal
from app.security.principal import Principal

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.get("/me", response_model=PrincipalResponse)
async def current_user(
    principal: Annotated[Principal, Depends(get_current_principal)],
) -> PrincipalResponse:
    return PrincipalResponse(
        user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        role=principal.role,
    )

