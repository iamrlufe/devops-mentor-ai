from abc import ABC, abstractmethod
from pathlib import Path

from app.documents.models import Document


class EmptyDocumentError(ValueError):
    """Raised when a file holds no text and cannot become a document."""


class DocumentLoader(ABC):

    @abstractmethod
    def load(self, path: Path) -> Document:
        """Read a single file and turn it into a document."""
        raise NotImplementedError
