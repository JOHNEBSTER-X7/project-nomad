"""PROJECT NOMAD local API — initial offline knowledge prototype."""

import os
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .knowledge import search_documents

app = FastAPI(
    title="PROJECT NOMAD API",
    version="0.1.0",
    description="Local-first API for the NOMAD offline knowledge prototype.",
)

allowed_origins = os.getenv(
    "NOMAD_CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "project-nomad-api", "mode": "local"}


@app.get("/api/knowledge/search")
def knowledge_search(
    q: str = Query(min_length=2, max_length=160),
    limit: int = Query(default=8, ge=1, le=20),
) -> dict:
    knowledge_dir = Path(
        os.getenv("NOMAD_KNOWLEDGE_DIR", str(Path(__file__).resolve().parents[1] / "knowledge"))
    )
    results = search_documents(q, knowledge_dir=knowledge_dir, limit=limit)
    return {
        "query": q,
        "mode": "local-lexical-search",
        "results": results,
        "count": len(results),
    }
