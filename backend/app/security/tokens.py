import uuid
from datetime import UTC, datetime, timedelta

import jwt
from jwt import InvalidTokenError

from app.core.config import Settings
from app.security.principal import Principal, Role


class TokenValidationError(ValueError):
    pass


class TokenService:
    algorithm = "HS256"

    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret
        self._issuer = settings.jwt_issuer
        self._audience = settings.jwt_audience
        self._minutes = settings.jwt_access_token_minutes

    def issue(self, principal: Principal, *, now: datetime | None = None) -> str:
        issued_at = now or datetime.now(UTC)
        claims = {
            "sub": str(principal.user_id),
            "tenant_id": str(principal.tenant_id),
            "role": principal.role.value,
            "iss": self._issuer,
            "aud": self._audience,
            "iat": issued_at,
            "exp": issued_at + timedelta(minutes=self._minutes),
        }
        return jwt.encode(claims, self._secret, algorithm=self.algorithm)

    def parse(self, token: str) -> Principal:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[self.algorithm],
                issuer=self._issuer,
                audience=self._audience,
                options={"require": ["sub", "tenant_id", "role", "exp", "iat"]},
            )
            return Principal(
                user_id=uuid.UUID(claims["sub"]),
                tenant_id=uuid.UUID(claims["tenant_id"]),
                role=Role(claims["role"]),
            )
        except (InvalidTokenError, KeyError, TypeError, ValueError) as error:
            raise TokenValidationError("access token is invalid or expired") from error

