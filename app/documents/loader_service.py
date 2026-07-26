from pathlib import Path

from app.documents.base import EmptyDocumentError
from app.documents.discovery import DocumentDiscovery
from app.documents.factory import DocumentLoaderFactory
from app.documents.models import Document


class DocumentLoaderService:

    @staticmethod
    def load_directory(directory: Path) -> list[Document]:
        """Load every supported document of the directory, skipping the empty ones."""
        documents: list[Document] = []

        for path in DocumentDiscovery.discover(directory):
            loader = DocumentLoaderFactory.create(path)

            try:
                documents.append(loader.load(path))
            except EmptyDocumentError:
                continue

        return documents
