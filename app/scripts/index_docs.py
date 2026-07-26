import sys
from pathlib import Path

from app.indexer.service import DocumentIndexer

DEFAULT_DIRECTORY = Path("docs")

directory = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIRECTORY

if not directory.is_dir():
    raise SystemExit(
        f"Documents directory was not found: {directory}\n"
        f"Usage: python -m app.scripts.index_docs [directory]"
    )

stats = DocumentIndexer.index(directory, on_step=print)

print(f"\nDocuments: {stats.documents}")
print(f"Chunks: {stats.chunks}")
print(f"Embeddings: {stats.embeddings}")
print(f"Indexed: {stats.indexed}")
