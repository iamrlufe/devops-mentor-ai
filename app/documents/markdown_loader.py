from pathlib import Path

from app.documents.base import DocumentLoader, EmptyDocumentError
from app.documents.models import Document

EXTENSION = ".md"


class MarkdownLoader(DocumentLoader):

    def load(self, path: Path) -> Document:
        text = path.read_text(encoding="utf-8").strip()

        if not text:
            raise EmptyDocumentError(f"Document is empty: {path}")

        return Document(
            id=path.stem,
            title=self._build_title(path, text),
            text=text,
            source=str(path),
        )

    @staticmethod
    def _build_title(path: Path, text: str) -> str:
        """Take the first Markdown heading, or fall back to the file name."""
        first_line = text.splitlines()[0].strip()

        if first_line.startswith("#"):
            title = first_line.lstrip("#").strip()
            if title:
                return title

        return path.stem
