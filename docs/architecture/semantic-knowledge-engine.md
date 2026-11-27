# NOMAD V0.3 — Offline semantic knowledge engine

## Purpose

V0.3 adds an optional local semantic retrieval path while preserving the V0.1 lexical search as a reliable fallback. It does not require a hosted embedding API or external network service.

## Design

- Approved Markdown and text files are split into bounded text chunks.
- A locally running Ollama embedding model creates vectors through its local `/api/embed` endpoint.
- Chunk text, source path, title and vector are stored in a local SQLite index.
- Search embeds the query locally, compares cosine similarity and returns the best chunk per source.
- If semantic retrieval is disabled, unindexed or unavailable, the API falls back to transparent lexical search.
- The index is rebuilt explicitly by an operator; it is not silently regenerated during a user request.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `NOMAD_EMBEDDINGS_PROVIDER` | `disabled` | Set to `ollama` to enable local embeddings |
| `NOMAD_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Local Ollama endpoint |
| `NOMAD_OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Configurable embedding model |
| `NOMAD_EMBEDDING_TIMEOUT_SECONDS` | `30` | Per-request embedding timeout |
| `NOMAD_INDEX_PATH` | `.nomad/knowledge.sqlite3` | SQLite index path |

The model name is a starting configuration, not a hardware recommendation. Evaluate language coverage, model licence, memory, latency and energy use on the intended device before selecting it for deployment.

## Build the index

Start the optional Ollama service and download a suitable embedding model, then run the indexing command from the backend directory:

```bash
NOMAD_EMBEDDINGS_PROVIDER=ollama python -m app.index_knowledge
```

The indexer reads only `.md` and `.txt` files under `NOMAD_KNOWLEDGE_DIR`, skips unreadable files and files above 2 MB, and stores vectors locally. Re-run after approved content changes. Do not index identifiable learner records or confidential material.

## API

- `GET /api/knowledge/index/status` reports whether semantic retrieval is enabled and how many chunks are indexed.
- `GET /api/knowledge/search?q=...` uses semantic retrieval when the local index is ready; otherwise it uses lexical retrieval. The response includes a mode field so clients can distinguish the path.

## Current limitations and gates

- This is a prototype, not a validated multilingual Nigerian-language retrieval system.
- Cosine similarity has no calibrated relevance threshold yet; results require evaluation.
- The first version returns the best chunk per source and does not implement reranking or hybrid score fusion.
- The local SQLite index is not encrypted and has no concurrent multi-writer design.
- No authentication, role-based access, rate limiting or administrator UI is added here.
- Ollama availability, model installation, hardware fit and energy consumption must be tested on target hardware.
- Prompt injection and unsafe source content remain risks for downstream generation.
- Before school use, complete adversarial retrieval tests, language-specific evaluations, access controls, safeguarding and privacy review.

V0.3 does not claim production readiness or a school deployment.
