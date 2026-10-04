from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.security.principal import Role
from app.security.tokens import TokenService


def test_demo_login_issues_a_signed_synthetic_tenant_identity() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/demo-login", json={"persona": "compliance"})

    assert response.status_code == 200
    body = response.json()
    assert body["demo_auth"] is True
    assert body["tenant_name"].endswith("Synthetic")
    assert body["user"]["role"] == "compliance"
    principal = TokenService(Settings()).parse(body["access_token"])
    assert principal.role == Role.COMPLIANCE
    assert str(principal.tenant_id) == body["user"]["tenant_id"]


def test_production_configuration_refuses_demo_auth() -> None:
    try:
        Settings(LEDGERLENS_ENV="production", jwt_secret="x" * 40, demo_auth_enabled=True)
    except ValueError as error:
        assert "DEMO_AUTH_ENABLED" in str(error)
    else:
        raise AssertionError("production settings accepted demo authentication")

