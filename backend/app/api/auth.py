from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.demo import DEMO_TENANT_ID, DEMO_TENANT_NAME, DEMO_USERS
from app.schemas.auth import DemoLoginRequest, DemoLoginResponse, PrincipalResponse
from app.security.dependencies import get_current_principal
from app.security.principal import Principal
from app.security.tokens import TokenService

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/demo-login", response_model=DemoLoginResponse)
async def demo_login(
    request: DemoLoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> DemoLoginResponse:
    if not settings.demo_auth_enabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if request.persona not in DEMO_USERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Demo persona must be analyst, compliance, or admin",
        )
    user_id, _email, display_name = DEMO_USERS[request.persona]
    principal = Principal(user_id, DEMO_TENANT_ID, request.persona)
    return DemoLoginResponse(
        access_token=TokenService(settings).issue(principal),
        user=PrincipalResponse(
            user_id=principal.user_id,
            tenant_id=principal.tenant_id,
            role=principal.role,
        ),
        display_name=display_name,
        tenant_name=DEMO_TENANT_NAME,
    )


@router.get("/me", response_model=PrincipalResponse)
async def current_user(
    principal: Annotated[Principal, Depends(get_current_principal)],
) -> PrincipalResponse:
    return PrincipalResponse(
        user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        role=principal.role,
    )
