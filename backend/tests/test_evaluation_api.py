import uuid

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.security.principal import Principal, Role
from app.security.tokens import TokenService


def token(role: Role) -> str:
    return TokenService(get_settings()).issue(Principal(uuid.uuid4(), uuid.uuid4(), role))


def test_evaluation_summary_is_real_and_permission_protected() -> None:
    with TestClient(app) as client:
        denied = client.get(
            "/api/v1/evaluation/summary",
            headers={"Authorization": f"Bearer {token(Role.ANALYST)}"},
        )
        allowed = client.get(
            "/api/v1/evaluation/summary",
            headers={"Authorization": f"Bearer {token(Role.COMPLIANCE)}"},
        )
        admin = client.get(
            "/api/v1/evaluation/summary",
            headers={"Authorization": f"Bearer {token(Role.ADMIN)}"},
        )

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert admin.status_code == 200
    assert admin.json() == allowed.json()
    assert allowed.json()["recall_at_3"] == 1.0
    assert allowed.json()["answer_term_coverage"] == 1.0
    assert allowed.json()["status"] == "passing"
