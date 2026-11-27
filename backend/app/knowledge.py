"""Small, dependency-light local Markdown/text search for NOMAD V0.1."""

from pathlib import Path
import re
from typing import Any

DEFAULT_KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"


def _tokens(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]{2,}", value.lower())}


def search_documents(
    query: str,
    knowledge_dir: Path = DEFAULT_KNOWLEDGE_DIR,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """Return lexical matches from local .md and .txt files.

    This is deliberately a transparent first prototype, not semantic search
    and not an AI-generated answer.
    """
    query_tokens = _tokens(query)
    if not query_tokens or not knowledge_dir.exists():
        return []

    matches: list[dict[str, Any]] = []
    for path in knowledge_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        document_tokens = _tokens(content)
        overlap = query_tokens.intersection(document_tokens)
        if not overlap:
            continue

        score = len(overlap) / max(len(query_tokens), 1)
        title = next(
            (line.lstrip("# ").strip() for line in content.splitlines() if line.startswith("#")),
            path.stem.replace("-", " ").title(),
        )
        excerpt = re.sub(r"\s+", " ", content).strip()[:420]
        matches.append(
            {
                "title": title,
                "source": path.relative_to(knowledge_dir).as_posix(),
                "excerpt": excerpt,
                "score": round(score, 3),
            }
        )

    return sorted(matches, key=lambda item: (-item["score"], item["source"]))[:limit]
