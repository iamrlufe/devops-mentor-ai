from app.chunking.base import Chunker
from app.chunking.markdown_chunker import MarkdownChunker


class ChunkerFactory:
    _chunker: Chunker | None = None

    @staticmethod
    def create() -> Chunker:
        """Return the chunker shared by the whole process."""
        if ChunkerFactory._chunker is None:
            ChunkerFactory._chunker = MarkdownChunker()

        return ChunkerFactory._chunker
