import sys
from pathlib import Path

from app.config import settings
from app.indexer.service import DocumentIndexer

DEFAULT_DIRECTORY = Path("docs")

directory = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIRECTORY
collection = sys.argv[2] if len(sys.argv) > 2 else ""

if not directory.is_dir():
    raise SystemExit(
        f"Documents directory was not found: {directory}\n"
        f"Usage: python -m app.scripts.index_docs [directory] [collection]"
    )

stats = DocumentIndexer.index(directory, on_step=print, collection=collection)

print(f"\nCollection: {collection or settings.qdrant_collection}")
print(f"Documents: {stats.documents}")
print(f"Chunks: {stats.chunks}")
print(f"Embeddings: {stats.embeddings}")
print(f"Indexed: {stats.indexed}")
