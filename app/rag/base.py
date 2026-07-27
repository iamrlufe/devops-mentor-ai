from abc import ABC, abstractmethod

from app.rag.models import Document


class Retriever(ABC):
    """Finds the documents that answer a question.

    A retriever is bound to one collection, so different agents can search
    different sets of documents through the same interface.
    """

    def __init__(self, collection: str = "") -> None:
        """Bind the retriever to a collection.

        Args:
            collection: Name of the collection to search. Empty means the
                shared collection configured for the platform.
        """
        self.collection = collection

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[Document]:
        """Return up to `limit` documents relevant to the query."""
        raise NotImplementedError
