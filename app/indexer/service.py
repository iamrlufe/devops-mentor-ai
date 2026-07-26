from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.chunking.models import Chunk
from app.chunking.service import ChunkService
from app.documents.loader_service import DocumentLoaderService
from app.embeddings.service import EmbeddingService
from app.rag import TEXT_KEY
from app.vectorstore.factory import VectorStoreFactory
from app.vectorstore.service import VectorStoreService

STEP_LOADING = "Loading..."
STEP_CHUNKING = "Chunking..."
STEP_EMBEDDING = "Embedding..."
STEP_UPLOADING = "Uploading..."
STEP_DONE = "Done."


@dataclass
class IndexStats:
    documents: int = 0
    chunks: int = 0
    embeddings: int = 0
    indexed: int = 0


class DocumentIndexer:

    @staticmethod
    def index(
        directory: Path,
        on_step: Callable[[str], None] | None = None,
    ) -> IndexStats:
        """Load, chunk, embed and store every document of the directory.

        The collection is dropped right before the upload, so the index never
        mixes the new documents with the previous ones.
        """
        report = on_step or (lambda step: None)

        report(STEP_LOADING)
        documents = DocumentLoaderService.load_directory(directory)

        if not documents:
            report(STEP_DONE)
            return IndexStats()

        report(STEP_CHUNKING)
        chunks = ChunkService.chunk_documents(documents)

        report(STEP_EMBEDDING)
        DocumentIndexer._attach_text(chunks)
        embeddings = EmbeddingService.embed_chunks(chunks)

        report(STEP_UPLOADING)
        VectorStoreFactory.create().delete_collection()
        indexed = VectorStoreService.index_embeddings(embeddings)

        report(STEP_DONE)

        return IndexStats(
            documents=len(documents),
            chunks=len(chunks),
            embeddings=len(embeddings),
            indexed=indexed,
        )

    @staticmethod
    def _attach_text(chunks: list[Chunk]) -> None:
        """Carry the chunk text into the metadata: the payload of a stored point
        holds the chunk id and the metadata, so this is what the retriever reads."""
        for chunk in chunks:
            chunk.metadata[TEXT_KEY] = chunk.text
