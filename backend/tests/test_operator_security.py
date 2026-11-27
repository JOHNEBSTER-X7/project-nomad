from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_operator_route_fails_closed_when_token_not_configured(monkeypatch):
    monkeypatch.delenv("NOMAD_OPERATOR_TOKEN", raising=False)
    assert client.get("/api/operator/status").status_code == 503

def test_operator_route_requires_bearer_token(monkeypatch):
    monkeypatch.setenv("NOMAD_OPERATOR_TOKEN", "a" * 40)
    response = client.get("/api/operator/status")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

def test_operator_route_rejects_wrong_token(monkeypatch):
    monkeypatch.setenv("NOMAD_OPERATOR_TOKEN", "a" * 40)
    response = client.get("/api/operator/status", headers={"Authorization": "Bearer " + "b" * 40})
    assert response.status_code == 401

def test_operator_route_accepts_configured_token(monkeypatch):
    monkeypatch.setenv("NOMAD_OPERATOR_TOKEN", "a" * 40)
    response = client.get("/api/operator/status", headers={"Authorization": "Bearer " + "a" * 40})
    assert response.status_code == 200
    assert response.json()["operator"]["role"] == "operator"
    assert response.json()["operator"]["authenticated"] is True
    assert "NOMAD_OPERATOR_TOKEN" not in response.text
