"""Build NOMAD's local semantic index: python -m app.index_knowledge."""
import os
from pathlib import Path
from .semantic_knowledge import build_semantic_index

def main():
    knowledge_dir = Path(os.getenv("NOMAD_KNOWLEDGE_DIR", str(Path(__file__).resolve().parents[1] / "knowledge")))
    result = build_semantic_index(knowledge_dir)
    print(f"Indexed {result['indexed_chunks']} chunks with {result['embedding_model']} into {result['database']}")

if __name__ == "__main__":
    main()
