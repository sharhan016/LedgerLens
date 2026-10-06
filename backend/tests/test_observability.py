import uuid

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.observability.http import request_metrics
from app.security.principal import Principal, Role
from app.security.tokens import TokenService


def access_token(role: Role) -> str:
    return TokenService(get_settings()).issue(Principal(uuid.uuid4(), uuid.uuid4(), role))


def test_request_metrics_record_only_route_status_count_and_latency() -> None:
    request_metrics.clear()
    with TestClient(app) as client:
        health = client.get("/health/live", headers={"X-Request-ID": "test-request"})
        denied = client.get(
            "/api/v1/operations/metrics",
            headers={"Authorization": f"Bearer {access_token(Role.VIEWER)}"},
        )
        compliance_denied = client.get(
            "/api/v1/operations/metrics",
            headers={"Authorization": f"Bearer {access_token(Role.COMPLIANCE)}"},
        )
        metrics = client.get(
            "/api/v1/operations/metrics",
            headers={"Authorization": f"Bearer {access_token(Role.ADMIN)}"},
        )

    assert health.headers["X-Request-ID"] == "test-request"
    assert float(health.headers["X-Response-Time-Ms"]) >= 0
    assert denied.status_code == 403
    assert compliance_denied.status_code == 403
    assert metrics.status_code == 200
    body = metrics.json()
    assert body["content_policy"] == "paths, status codes, counts, and latency only"
    serialized = str(body)
    assert "authorization" not in serialized.lower()
    assert "bearer" not in serialized.lower()
    assert any(item["route"] == "/health/live" for item in body["metrics"])
