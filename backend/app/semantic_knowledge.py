"""Optional offline semantic retrieval backed by a local Ollama embedding model.

The lexical search remains the dependable fallback. This module stores only
approved document chunks and embeddings in a local SQLite database.
"""
import json
import math
import os
import re
import sqlite3
from pathlib import Path
from urllib.request import Request, urlopen

from .knowledge import search_documents

def _config():
    return (
        os.getenv("NOMAD_EMBEDDINGS_PROVIDER", "disabled").strip().lower(),
        os.getenv("NOMAD_OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/"),
        os.getenv("NOMAD_OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        float(os.getenv("NOMAD_EMBEDDING_TIMEOUT_SECONDS", "30")),
        Path(os.getenv("NOMAD_INDEX_PATH", ".nomad/knowledge.sqlite3")),
    )

def _connect(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("""CREATE TABLE IF NOT EXISTS knowledge_chunks (
        id INTEGER PRIMARY KEY, source TEXT NOT NULL, title TEXT NOT NULL,
        chunk_index INTEGER NOT NULL, content TEXT NOT NULL,
        embedding TEXT NOT NULL, UNIQUE(source, chunk_index)
    )""")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_chunks(source)")
    return connection

def _embed(text: str) -> list[float]:
    provider, base, model, timeout, _ = _config()
    if provider != "ollama":
        raise RuntimeError("Local embeddings are disabled. Set NOMAD_EMBEDDINGS_PROVIDER=ollama.")
    body = json.dumps({"model": model, "input": text}).encode("utf-8")
    request = Request(f"{base}/api/embed", data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        vectors = payload.get("embeddings") or []
        vector = vectors[0] if vectors else payload.get("embedding")
        if not isinstance(vector, list) or not vector:
            raise RuntimeError("Embedding runtime returned no vector.")
        return [float(value) for value in vector]
    except (OSError, ValueError, KeyError) as exc:
        raise RuntimeError("Local embedding runtime could not complete the request.") from exc

def _chunks(content: str, max_chars: int = 1200, overlap: int = 160) -> list[str]:
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", content) if part.strip()]
    chunks, current = [], ""
    for paragraph in paragraphs:
        while len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars - overlap:]
        candidate = f"{current} {paragraph}".strip()
        if len(candidate) > max_chars and current:
            chunks.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks

def build_semantic_index(knowledge_dir: Path) -> dict:
    """Rebuild the local index atomically; intended for an administrator CLI."""
    provider, _, model, _, db_path = _config()
    if provider != "ollama":
        raise RuntimeError("Configure NOMAD_EMBEDDINGS_PROVIDER=ollama before indexing.")
    documents = []
    for path in sorted(knowledge_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if len(content) > 2_000_000:
            continue
        title = next((line.lstrip("# ").strip() for line in content.splitlines() if line.startswith("#")),
                     path.stem.replace("-", " ").title())
        for index, chunk in enumerate(_chunks(content)):
            documents.append((path.relative_to(knowledge_dir).as_posix(), title, index, chunk, _embed(chunk)))
    connection = _connect(db_path)
    try:
        with connection:
            connection.execute("DELETE FROM knowledge_chunks")
            connection.executemany(
                "INSERT INTO knowledge_chunks(source,title,chunk_index,content,embedding) VALUES(?,?,?,?,?)",
                [(s,t,i,c,json.dumps(v)) for s,t,i,c,v in documents],
            )
            connection.execute("CREATE TABLE IF NOT EXISTS index_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            connection.execute("INSERT OR REPLACE INTO index_metadata(key,value) VALUES('embedding_model',?)", (model,))
    finally:
        connection.close()
    return {"indexed_chunks": len(documents), "embedding_model": model, "database": str(db_path)}

def _cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return 0.0
    denominator = math.sqrt(sum(x*x for x in left)) * math.sqrt(sum(y*y for y in right))
    return sum(x*y for x,y in zip(left,right)) / denominator if denominator else 0.0

def semantic_index_status() -> dict:
    provider, _, model, _, db_path = _config()
    if provider != "ollama":
        return {"enabled": False, "provider": "disabled", "indexed_chunks": 0, "message": "Semantic retrieval is disabled; lexical search remains available."}
    if not db_path.exists():
        return {"enabled": True, "provider": "ollama", "model": model, "indexed_chunks": 0, "message": "Semantic index has not been built."}
    try:
        with _connect(db_path) as connection:
            count = connection.execute("SELECT COUNT(*) FROM knowledge_chunks").fetchone()[0]
        return {"enabled": True, "provider": "ollama", "model": model, "indexed_chunks": count,
                "message": "Semantic index ready." if count else "Semantic index is empty."}
    except sqlite3.Error:
        return {"enabled": True, "provider": "ollama", "model": model, "indexed_chunks": 0, "message": "Semantic index could not be read."}

def search_knowledge(query: str, knowledge_dir: Path, limit: int = 8) -> tuple[list[dict], str]:
    """Use local vector retrieval when an index exists; otherwise lexical fallback."""
    status = semantic_index_status()
    if not status.get("enabled") or not status.get("indexed_chunks"):
        return search_documents(query, knowledge_dir=knowledge_dir, limit=limit), "local-lexical-search"
    try:
        vector = _embed(query)
        _, _, _, _, db_path = _config()
        with _connect(db_path) as connection:
            rows = connection.execute("SELECT source,title,content,embedding FROM knowledge_chunks").fetchall()
        best = {}
        for source,title,content,stored in rows:
            score = _cosine(vector, json.loads(stored))
            if source not in best or score > best[source]["score"]:
                best[source] = {"title": title, "source": source, "excerpt": content[:420], "score": round(score, 4)}
        results = sorted(best.values(), key=lambda item: (-item["score"], item["source"]))[:limit]
        return results, "local-ollama-semantic-search"
    except (RuntimeError, OSError, ValueError, sqlite3.Error, json.JSONDecodeError):
        return search_documents(query, knowledge_dir=knowledge_dir, limit=limit), "local-lexical-fallback"
