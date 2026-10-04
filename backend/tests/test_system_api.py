from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness_is_explicit() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ledgerlens-api"}


def test_system_status_does_not_claim_planned_features() -> None:
    response = client.get("/api/v1/system/status")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "foundation_ready"
    assert body["capabilities"][0] == {
        "name": "API foundation",
        "status": "ready",
        "vertex_task": "T-01",
    }
    assert [item["status"] for item in body["capabilities"]] == [
        "ready",
        "ready",
        "ready",
        "planned",
        "planned",
    ]
