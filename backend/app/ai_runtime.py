"""Optional local Ollama adapter. No hosted AI provider is supported here."""
import json
import os
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

def _config():
    return (os.getenv("NOMAD_OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/"), os.getenv("NOMAD_OLLAMA_MODEL", "llama3.2:3b"), float(os.getenv("NOMAD_AI_TIMEOUT_SECONDS", "45")))

def runtime_status():
    if os.getenv("NOMAD_AI_PROVIDER", "disabled").strip().lower() != "ollama":
        return {"enabled": False, "provider": "disabled", "available": False, "message": "Local AI is disabled. Configure NOMAD_AI_PROVIDER=ollama to enable it."}
    base, model, timeout = _config()
    try:
        with urlopen(Request(f"{base}/api/tags", headers={"Accept": "application/json"}), timeout=min(timeout, 3.0)) as response:
            payload = json.loads(response.read().decode("utf-8"))
        models = [item.get("name", "") for item in payload.get("models", [])]
        available = any(name == model or name.split(":")[0] == model.split(":")[0] for name in models)
        return {"enabled": True, "provider": "ollama", "available": available, "model": model, "installed_models": models, "message": "Local model is ready." if available else "Ollama is reachable, but the configured model is not installed."}
    except (OSError, ValueError, URLError, HTTPError, TimeoutError):
        return {"enabled": True, "provider": "ollama", "available": False, "model": model, "installed_models": [], "message": "Local Ollama runtime is not reachable."}

def generate_local_answer(question, context):
    if os.getenv("NOMAD_AI_PROVIDER", "disabled").strip().lower() != "ollama":
        raise RuntimeError("Local AI is disabled.")
    base, model, timeout = _config()
    sources = "\n\n".join(f"[{i}] {item['title']} ({item['source']})\n{item['excerpt']}" for i, item in enumerate(context, 1))
    prompt = ("You are the offline-first PROJECT NOMAD learning assistant. Answer using only the supplied local source excerpts. If they do not contain the answer, say the local library does not provide enough information. Do not invent facts. Cite supporting excerpts inline as [1], [2]. Use clear, age-appropriate language.\n\nLOCAL SOURCES:\n" + (sources or "No matching local sources.") + "\n\nQUESTION:\n" + question)
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    request = Request(f"{base}/api/generate", data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, URLError, HTTPError, TimeoutError) as exc:
        raise RuntimeError("The local AI runtime could not complete the request.") from exc
    answer = payload.get("response", "").strip()
    if not answer:
        raise RuntimeError("The local AI runtime returned an empty answer.")
    return answer
