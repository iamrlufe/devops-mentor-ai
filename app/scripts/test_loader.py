import sys
from pathlib import Path

from app.documents.discovery import DocumentDiscovery
from app.documents.loader_service import DocumentLoaderService

DEFAULT_DIRECTORY = Path(__file__).resolve().parents[2] / "docs"

directory = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIRECTORY

if not directory.is_dir():
    raise SystemExit(
        f"Documents directory was not found: {directory}\n"
        f"Usage: python -m app.scripts.test_loader [directory]"
    )

print(f"Directory: {directory}")

paths = DocumentDiscovery.discover(directory)
print(f"Found files: {len(paths)}")

for path in paths:
    print(f"  {path}")

documents = DocumentLoaderService.load_directory(directory)
print(f"\nLoaded documents: {len(documents)}")

for document in documents:
    print(f"\nid: {document.id}")
    print(f"title: {document.title}")
    print(f"source: {document.source}")
    print(f"length: {len(document.text)}")
