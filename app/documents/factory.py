from pathlib import Path

from app.documents.base import DocumentLoader
from app.documents.markdown_loader import EXTENSION as MARKDOWN_EXTENSION
from app.documents.markdown_loader import MarkdownLoader

LOADERS: dict[str, type[DocumentLoader]] = {
    MARKDOWN_EXTENSION: MarkdownLoader,
}


class DocumentLoaderFactory:

    @staticmethod
    def create(path: Path) -> DocumentLoader:
        """Pick a loader by file extension."""
        loader = LOADERS.get(path.suffix.lower())

        if loader is None:
            raise ValueError(f"Unsupported document format: {path.name}")

        return loader()
