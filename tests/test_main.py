from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ops_summary_endpoint():
    response = client.get("/ops/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_gates" in data
    assert "critical_crowd_gates" in data
    assert "closed_gates" in data
    assert "transport_status" in data
    assert isinstance(data["critical_crowd_gates"], list)
    assert isinstance(data["closed_gates"], list)


def test_chat_endpoint_returns_valid_response():
    payload = {
        "message": "where is the nearest exit",
        "profile": {"seat_zone": "Zone 1", "mobility_need": "none"},
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "detected_intent" in data
    assert "detected_language" in data