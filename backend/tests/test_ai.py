from fastapi.testclient import TestClient
from app.main import app
from app import main

client = TestClient(app)

def test_ai_status_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("NOMAD_AI_PROVIDER", raising=False)
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    assert response.json()["enabled"] is False
    assert response.json()["provider"] == "disabled"

def test_ai_answer_is_unavailable_when_disabled(monkeypatch):
    monkeypatch.delenv("NOMAD_AI_PROVIDER", raising=False)
    assert client.post("/api/ai/answer", json={"question": "Explain offline learning"}).status_code == 503

def test_ai_answer_uses_local_sources_and_reports_citations(monkeypatch):
    monkeypatch.setenv("NOMAD_AI_PROVIDER", "ollama")
    monkeypatch.setattr(main, "runtime_status", lambda: {"enabled": True, "provider": "ollama", "available": True, "model": "test-model"})
    monkeypatch.setattr(main, "generate_local_answer", lambda question, context: "Use local resources [1].")
    response = client.post("/api/ai/answer", json={"question": "offline learning"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "local-ollama-grounded"
    assert payload["answer"].endswith("[1].")
    assert payload["source_count"] >= 1
    assert payload["sources"][0]["source"]

def test_ai_does_not_generate_without_matching_local_sources(monkeypatch):
    monkeypatch.setenv("NOMAD_AI_PROVIDER", "ollama")
    monkeypatch.setattr(main, "runtime_status", lambda: {"enabled": True, "provider": "ollama", "available": True})
    monkeypatch.setattr(main, "search_documents", lambda *args, **kwargs: [])
    def fail_if_called(*args, **kwargs):
        raise AssertionError("Model must not be called without local evidence")
    monkeypatch.setattr(main, "generate_local_answer", fail_if_called)
    response = client.post("/api/ai/answer", json={"question": "question with no local matches"})
    assert response.status_code == 200
    assert response.json()["mode"] == "local-library-insufficient"
    assert response.json()["source_count"] == 0

def test_ai_answer_validates_question_length():
    assert client.post("/api/ai/answer", json={"question": "x"}).status_code == 422
