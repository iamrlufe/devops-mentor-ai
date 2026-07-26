from abc import ABC, abstractmethod

from app.chunking.models import Chunk
from app.documents.models import Document


class Chunker(ABC):

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """Split a document into chunks, keeping the whole text."""
        raise NotImplementedError
