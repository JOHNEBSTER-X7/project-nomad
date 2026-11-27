import json
from pathlib import Path
from app import semantic_knowledge as semantic

def test_chunking_splits_large_documents():
    chunks = semantic._chunks("A" * 2600, max_chars=1000, overlap=100)
    assert len(chunks) >= 3
    assert all(len(chunk) <= 1000 for chunk in chunks)

def test_index_build_and_semantic_search_use_local_vectors(tmp_path, monkeypatch):
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    (knowledge / "solar.md").write_text("# Solar power\n\nSolar panels convert sunlight into electricity.", encoding="utf-8")
    db = tmp_path / "index.sqlite3"
    monkeypatch.setenv("NOMAD_EMBEDDINGS_PROVIDER", "ollama")
    monkeypatch.setenv("NOMAD_INDEX_PATH", str(db))
    monkeypatch.setenv("NOMAD_OLLAMA_EMBED_MODEL", "test-embed")
    monkeypatch.setattr(semantic, "_embed", lambda text: [1.0, 0.0])
    result = semantic.build_semantic_index(knowledge)
    assert result["indexed_chunks"] == 1
    found, mode = semantic.search_knowledge("sunlight", knowledge, limit=3)
    assert mode == "local-ollama-semantic-search"
    assert found[0]["source"] == "solar.md"

def test_lexical_fallback_when_semantic_is_disabled(tmp_path, monkeypatch):
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    (knowledge / "learning.md").write_text("# Offline learning\n\nLocal resources support education.", encoding="utf-8")
    monkeypatch.delenv("NOMAD_EMBEDDINGS_PROVIDER", raising=False)
    results, mode = semantic.search_knowledge("offline learning", knowledge)
    assert mode == "local-lexical-search"
    assert results

def test_model_mismatch_falls_back_to_lexical(tmp_path, monkeypatch):
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    (knowledge / "solar.md").write_text("# Solar power\\n\\nSolar energy is renewable.", encoding="utf-8")
    db = tmp_path / "index.sqlite3"
    monkeypatch.setenv("NOMAD_EMBEDDINGS_PROVIDER", "ollama")
    monkeypatch.setenv("NOMAD_INDEX_PATH", str(db))
    monkeypatch.setenv("NOMAD_OLLAMA_EMBED_MODEL", "model-b")
    monkeypatch.setattr(semantic, "_embed", lambda text: [1.0, 0.0])
    # Build with model A, then switch the configured model.
    monkeypatch.setenv("NOMAD_OLLAMA_EMBED_MODEL", "model-a")
    semantic.build_semantic_index(knowledge)
    monkeypatch.setenv("NOMAD_OLLAMA_EMBED_MODEL", "model-b")
    results, mode = semantic.search_knowledge("solar", knowledge)
    assert mode == "local-lexical-fallback"
    assert results

def test_semantic_threshold_can_return_no_evidence(tmp_path, monkeypatch):
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    (knowledge / "solar.md").write_text("# Solar power\\n\\nSolar panels generate electricity.", encoding="utf-8")
    db = tmp_path / "index.sqlite3"
    monkeypatch.setenv("NOMAD_EMBEDDINGS_PROVIDER", "ollama")
    monkeypatch.setenv("NOMAD_INDEX_PATH", str(db))
    monkeypatch.setenv("NOMAD_OLLAMA_EMBED_MODEL", "test-embed")
    monkeypatch.setenv("NOMAD_SEMANTIC_MIN_SCORE", "0.9")
    monkeypatch.setattr(semantic, "_embed", lambda text: [1.0, 0.0] if text.startswith("#") else [0.0, 1.0])
    semantic.build_semantic_index(knowledge)
    results, mode = semantic.search_knowledge("completely unrelated", knowledge)
    assert mode == "local-ollama-semantic-search"
    assert results == []
