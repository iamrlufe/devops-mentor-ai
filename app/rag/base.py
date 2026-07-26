from abc import ABC, abstractmethod

from app.rag.models import Document


class Retriever(ABC):

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[Document]:
        """Return up to `limit` documents relevant to the query."""
        raise NotImplementedError
