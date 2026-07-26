from abc import ABC, abstractmethod

from app.embeddings.models import Embedding
from app.vectorstore.models import SearchResult


class VectorStore(ABC):

    @abstractmethod
    def create_collection(self, vector_size: int) -> None:
        """Create the collection if it does not exist yet."""
        raise NotImplementedError

    @abstractmethod
    def upsert(self, embeddings: list[Embedding]) -> None:
        """Store the embeddings, replacing the ones with the same chunk id."""
        raise NotImplementedError

    @abstractmethod
    def search(self, vector: list[float], limit: int = 5) -> list[SearchResult]:
        """Return the closest chunks to the query vector."""
        raise NotImplementedError

    @abstractmethod
    def delete_collection(self) -> None:
        """Drop the collection with everything it holds."""
        raise NotImplementedError
