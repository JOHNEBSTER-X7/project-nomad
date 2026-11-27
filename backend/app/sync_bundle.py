"""Validated, operator-triggered import of staged offline knowledge bundles.

No remote URLs are fetched. The operator stages files locally; a manifest
declares source IDs and SHA-256 hashes. Only configured source IDs are accepted.
"""
import hashlib
import json
import os
import re
from pathlib import Path

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")
_ALLOWED_SUFFIXES = {".md", ".txt"}
_MANIFEST_LIMIT = 128_000
_DEFAULT_FILE_LIMIT = 2_000_000
_MAX_SOURCES = 100

def _inbox() -> Path:
    return Path(os.getenv("NOMAD_SYNC_INBOX", "/sync-inbox")).resolve()

def _allowed_sources() -> set[str]:
    return {item.strip() for item in os.getenv("NOMAD_SYNC_ALLOWED_SOURCE_IDS", "").split(",") if item.strip()}

def _validated_bundle(bundle_id: str) -> list[dict]:
    if not _ID.fullmatch(bundle_id):
        raise ValueError("Invalid bundle identifier.")
    inbox = _inbox()
    if not inbox.exists() or not inbox.is_dir():
        raise FileNotFoundError("The configured sync inbox is unavailable.")
    bundle_path = inbox / bundle_id
    bundle = bundle_path.resolve()
    if bundle.parent != inbox or not bundle.is_dir() or bundle_path.is_symlink():
        raise FileNotFoundError("The requested staged bundle was not found.")
    manifest_path = bundle / "manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file() or manifest_path.stat().st_size > _MANIFEST_LIMIT:
        raise ValueError("Bundle manifest is missing, unsafe or too large.")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Bundle manifest must be valid UTF-8 JSON.") from exc
    if not isinstance(manifest, dict) or manifest.get("version") != 1 or manifest.get("bundle_id") != bundle_id:
        raise ValueError("Unsupported manifest version or bundle identifier mismatch.")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources or len(sources) > _MAX_SOURCES:
        raise ValueError("Manifest must contain between 1 and 100 sources.")
    allowed = _allowed_sources()
    if not allowed:
        raise PermissionError("No source IDs are allowlisted. Configure NOMAD_SYNC_ALLOWED_SOURCE_IDS first.")
    max_bytes = int(os.getenv("NOMAD_SYNC_MAX_FILE_BYTES", str(_DEFAULT_FILE_LIMIT)))
    if max_bytes < 1 or max_bytes > 20_000_000:
        raise ValueError("NOMAD_SYNC_MAX_FILE_BYTES must be between 1 and 20000000.")
    seen = set()
    validated = []
    for item in sources:
        if not isinstance(item, dict):
            raise ValueError("Each manifest source must be an object.")
        source_id, filename, expected = item.get("source_id"), item.get("file"), item.get("sha256")
        if not isinstance(source_id, str) or source_id not in allowed:
            raise PermissionError("Manifest contains a source ID that is not allowlisted.")
        if source_id in seen:
            raise ValueError("Duplicate source IDs are not permitted in one bundle.")
        seen.add(source_id)
        if not isinstance(filename, str) or Path(filename).name != filename or filename in {"", ".", ".."}:
            raise ValueError("Source filenames must be simple filenames without path components.")
        suffix = Path(filename).suffix.lower()
        if suffix not in _ALLOWED_SUFFIXES:
            raise ValueError("Only Markdown and plain-text knowledge files are accepted.")
        if not isinstance(expected, str) or not _SHA256.fullmatch(expected):
            raise ValueError("Each source must declare a valid SHA-256 digest.")
        source_path = bundle / filename
        if source_path.is_symlink() or not source_path.is_file() or source_path.resolve().parent != bundle:
            raise ValueError("A declared source file is missing or unsafe.")
        if source_path.stat().st_size > max_bytes:
            raise ValueError("A source file exceeds the configured size limit.")
        content = source_path.read_bytes()
        if b"\x00" in content:
            raise ValueError("Binary content is not accepted as a knowledge document.")
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Knowledge documents must be valid UTF-8.") from exc
        actual = hashlib.sha256(content).hexdigest()
        if actual != expected.lower():
            raise ValueError("SHA-256 verification failed for a staged source.")
        target_name = f"sync-{source_id}-{actual[:16]}{suffix}"
        validated.append({"source_id": source_id, "file": filename, "sha256": actual, "bytes": len(content), "target_name": target_name, "content": content})
    return validated

def preview_bundle(bundle_id: str) -> dict:
    items = _validated_bundle(bundle_id)
    return {"bundle_id": bundle_id, "approved": True, "imported": False, "source_count": len(items), "sources": [{k: v for k, v in item.items() if k != "content"} | {"status": "verified_pending_import"} for item in items]}

def import_bundle(bundle_id: str, knowledge_dir: Path) -> dict:
    items = _validated_bundle(bundle_id)
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    created = []
    results = []
    try:
        for item in items:
            target = knowledge_dir / item["target_name"]
            if target.exists():
                if hashlib.sha256(target.read_bytes()).hexdigest() != item["sha256"]:
                    raise ValueError("An existing imported file failed its integrity check.")
                state = "already_present"
            else:
                with target.open("xb") as stream:
                    stream.write(item["content"])
                created.append(target)
                state = "imported"
            results.append({"source_id": item["source_id"], "file": item["target_name"], "sha256": item["sha256"], "bytes": item["bytes"], "status": state})
    except Exception:
        for path in created:
            try:
                path.unlink()
            except OSError:
                pass
        raise
    return {"bundle_id": bundle_id, "approved": True, "imported": True, "source_count": len(results), "sources": results, "next_step": "Rebuild the semantic index if semantic retrieval is enabled."}
