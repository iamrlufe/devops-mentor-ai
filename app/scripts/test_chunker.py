import sys
from pathlib import Path

from app.chunking.factory import ChunkerFactory
from app.chunking.service import ChunkService
from app.documents.loader_service import DocumentLoaderService
from app.documents.models import Document

DEFAULT_DIRECTORY = Path(__file__).resolve().parents[2] / "docs"
PREVIEW_LENGTH = 100

SAMPLE_DOCUMENT = Document(
    id="sample",
    title="Sample document",
    text=(
        "Docker packages an application together with its dependencies. "
        "A Dockerfile describes the image, and `docker build` produces it. "
    ) * 30,
    source="<built-in sample>",
)

directory = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIRECTORY

if directory.is_dir():
    documents = DocumentLoaderService.load_directory(directory)
else:
    documents = []

if not documents:
    print(f"No documents found in {directory}, using the built-in sample.\n")
    documents = [SAMPLE_DOCUMENT]

print(f"Chunker: {type(ChunkerFactory.create()).__name__}")
print(f"Documents: {len(documents)}")

for document in documents:
    chunks = ChunkService.chunk_documents([document])

    print(f"\nDocument: {document.title}")
    print(f"  id: {document.id}")
    print(f"  source: {document.source}")
    print(f"  length: {len(document.text)}")
    print(f"  chunks: {len(chunks)}")

    for chunk in chunks:
        preview = chunk.text[:PREVIEW_LENGTH].replace("\n", " ")
        print(f"    {chunk.id} | size: {len(chunk.text)} | {preview}")

print(f"\nTotal chunks: {len(ChunkService.chunk_documents(documents))}")
