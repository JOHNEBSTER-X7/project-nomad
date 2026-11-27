from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_local_service():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "project-nomad-api",
        "mode": "local",
    }


def test_search_returns_local_knowledge_result():
    response = client.get(
        "/api/knowledge/search",
        params={"q": "offline learning", "limit": 5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "local-lexical-search"
    assert payload["count"] >= 1
    assert any("offline" in item["source"] for item in payload["results"])


def test_search_rejects_too_short_query():
    response = client.get("/api/knowledge/search", params={"q": "a"})
    assert response.status_code == 422
