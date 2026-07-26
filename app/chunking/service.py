from app.chunking.factory import ChunkerFactory
from app.chunking.models import Chunk
from app.documents.models import Document


class ChunkService:

    @staticmethod
    def chunk_documents(documents: list[Document]) -> list[Chunk]:
        """Split every document and return all chunks in document order."""
        chunker = ChunkerFactory.create()
        chunks: list[Chunk] = []

        for document in documents:
            chunks.extend(chunker.chunk(document))

        return chunks
