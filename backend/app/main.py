"""PROJECT NOMAD local API — offline knowledge and optional local AI."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .ai_runtime import generate_local_answer, runtime_status
from .semantic_knowledge import search_knowledge, semantic_index_status

app = FastAPI(title="PROJECT NOMAD API", version="0.3.0", description="Local-first API for offline knowledge retrieval and optional local AI.")
allowed_origins = os.getenv("NOMAD_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in allowed_origins if o.strip()], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    limit: int = Field(default=5, ge=1, le=10)

def _knowledge_dir():
    return Path(os.getenv("NOMAD_KNOWLEDGE_DIR", str(Path(__file__).resolve().parents[1] / "knowledge")))

@app.get("/health")
def health():
    return {"status": "ok", "service": "project-nomad-api", "mode": "local"}

@app.get("/api/knowledge/search")
def knowledge_search(q: str = Query(min_length=2, max_length=160), limit: int = Query(default=8, ge=1, le=20)):
    results, mode = search_knowledge(q, knowledge_dir=_knowledge_dir(), limit=limit)
    return {"query": q, "mode": mode, "results": results, "count": len(results)}

@app.get("/api/knowledge/index/status")
def knowledge_index_status():
    return semantic_index_status()

@app.get("/api/ai/status")
def ai_status():
    return runtime_status()

@app.post("/api/ai/answer")
def ai_answer(request: AskRequest):
    status = runtime_status()
    if not status.get("enabled"):
        raise HTTPException(status_code=503, detail="Local AI is disabled. Enable a local runtime first.")
    if not status.get("available"):
        raise HTTPException(status_code=503, detail=status.get("message", "Local AI is unavailable."))
    sources, retrieval_mode = search_knowledge(request.question, knowledge_dir=_knowledge_dir(), limit=request.limit)
    if not sources:
        return {"answer": "The local knowledge library does not contain matching material to answer this question.", "mode": "local-library-insufficient", "retrieval_mode": retrieval_mode, "sources": [], "source_count": 0, "notice": "No model was called because no supporting local source was found."}
    try:
        answer = generate_local_answer(request.question, sources)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"answer": answer, "mode": "local-ollama-grounded", "retrieval_mode": retrieval_mode, "sources": [{"title": item["title"], "source": item["source"]} for item in sources], "source_count": len(sources), "notice": "AI-generated response from the configured local model; verify important information with a qualified educator. Citations in the answer are model-generated and require checking against the listed sources."}
