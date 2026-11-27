import hashlib
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
TOKEN = "operator-secret-" + "x" * 40

def _bundle(tmp_path, monkeypatch, source_id="approved-curriculum", filename="lesson.md", content="# Offline learning\nApproved material.\n", digest=None):
    inbox = tmp_path / "inbox"
    folder = inbox / "bundle-001"
    folder.mkdir(parents=True)
    data = content.encode("utf-8")
    (folder / filename).write_bytes(data)
    manifest = {"version": 1, "bundle_id": "bundle-001", "sources": [{"source_id": source_id, "file": filename, "sha256": digest or hashlib.sha256(data).hexdigest()}]}
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setenv("NOMAD_SYNC_INBOX", str(inbox))
    monkeypatch.setenv("NOMAD_SYNC_ALLOWED_SOURCE_IDS", "approved-curriculum")
    monkeypatch.setenv("NOMAD_OPERATOR_TOKEN", TOKEN)
    return folder

def _auth():
    return {"Authorization": "Bearer " + TOKEN}

def test_sync_preview_requires_operator_authentication(tmp_path, monkeypatch):
    _bundle(tmp_path, monkeypatch)
    response = client.post("/api/operator/sync/preview", json={"bundle_id": "bundle-001"})
    assert response.status_code == 401

def test_sync_preview_verifies_allowlisted_bundle(tmp_path, monkeypatch):
    _bundle(tmp_path, monkeypatch)
    response = client.post("/api/operator/sync/preview", json={"bundle_id": "bundle-001"}, headers=_auth())
    assert response.status_code == 200
    assert response.json()["approved"] is True
    assert response.json()["imported"] is False
    assert response.json()["sources"][0]["status"] == "verified_pending_import"

def test_sync_import_is_idempotent(tmp_path, monkeypatch):
    _bundle(tmp_path, monkeypatch)
    knowledge = tmp_path / "knowledge"
    monkeypatch.setenv("NOMAD_KNOWLEDGE_DIR", str(knowledge))
    payload = {"bundle_id": "bundle-001"}
    first = client.post("/api/operator/sync/import", json=payload, headers=_auth())
    second = client.post("/api/operator/sync/import", json=payload, headers=_auth())
    assert first.status_code == 200
    assert first.json()["sources"][0]["status"] == "imported"
    assert second.status_code == 200
    assert second.json()["sources"][0]["status"] == "already_present"
    assert len(list(knowledge.glob("sync-*.md"))) == 1

def test_sync_rejects_non_allowlisted_source(tmp_path, monkeypatch):
    _bundle(tmp_path, monkeypatch, source_id="unknown-source")
    response = client.post("/api/operator/sync/preview", json={"bundle_id": "bundle-001"}, headers=_auth())
    assert response.status_code == 403

def test_sync_rejects_hash_mismatch(tmp_path, monkeypatch):
    _bundle(tmp_path, monkeypatch, digest="0" * 64)
    response = client.post("/api/operator/sync/preview", json={"bundle_id": "bundle-001"}, headers=_auth())
    assert response.status_code == 400

def test_sync_rejects_path_traversal_filename(tmp_path, monkeypatch):
    _bundle(tmp_path, monkeypatch, filename="../lesson.md")
    response = client.post("/api/operator/sync/preview", json={"bundle_id": "bundle-001"}, headers=_auth())
    assert response.status_code == 400

def test_sync_rejects_missing_allowlist(tmp_path, monkeypatch):
    _bundle(tmp_path, monkeypatch)
    monkeypatch.setenv("NOMAD_SYNC_ALLOWED_SOURCE_IDS", "")
    response = client.post("/api/operator/sync/preview", json={"bundle_id": "bundle-001"}, headers=_auth())
    assert response.status_code == 403
