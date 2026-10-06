import uuid
from datetime import UTC, datetime

import jwt
import pytest

from app.core.config import Settings
from app.security.principal import Permission, Principal, Role
from app.security.tokens import TokenService, TokenValidationError


def settings() -> Settings:
    return Settings(
        LEDGERLENS_ENV="test",
        jwt_secret="test-secret-with-at-least-thirty-two-characters",
    )


def test_signed_token_round_trip_preserves_tenant_and_role() -> None:
    principal = Principal(uuid.uuid4(), uuid.uuid4(), Role.COMPLIANCE)
    service = TokenService(settings())

    token = service.issue(principal, now=datetime(2030, 1, 1, tzinfo=UTC))
    claims = jwt.decode(token, options={"verify_signature": False})

    assert claims["tenant_id"] == str(principal.tenant_id)
    assert claims["role"] == "compliance"
    assert principal.can(Permission.AUDIT_READ)
    assert not principal.can(Permission.OPERATIONS_READ)
    assert Principal(principal.user_id, principal.tenant_id, Role.ADMIN).can(
        Permission.OPERATIONS_READ
    )
    assert not Principal(principal.user_id, principal.tenant_id, Role.VIEWER).can(
        Permission.DOCUMENTS_WRITE
    )


def test_invalid_token_is_rejected_without_leaking_decode_details() -> None:
    with pytest.raises(TokenValidationError, match="invalid or expired"):
        TokenService(settings()).parse("not-a-token")
