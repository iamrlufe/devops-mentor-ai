from app.chunking.base import Chunker
from app.chunking.models import Chunk
from app.documents.models import Document

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
STEP = CHUNK_SIZE - CHUNK_OVERLAP


class MarkdownChunker(Chunker):
    """Splits a document into fixed size windows that overlap, so nothing is lost."""

    def chunk(self, document: Document) -> list[Chunk]:
        text = document.text

        if not text:
            return []

        chunks: list[Chunk] = []
        start = 0

        while start < len(text):
            chunks.append(
                self._build_chunk(document, text[start:start + CHUNK_SIZE], len(chunks))
            )

            if start + CHUNK_SIZE >= len(text):
                break

            start += STEP

        return chunks

    @staticmethod
    def _build_chunk(document: Document, text: str, index: int) -> Chunk:
        order = index + 1

        return Chunk(
            id=f"{document.id}-{order:04d}",
            document_id=document.id,
            text=text,
            order=order,
            metadata={
                "title": document.title,
                "source": document.source,
            },
        )
