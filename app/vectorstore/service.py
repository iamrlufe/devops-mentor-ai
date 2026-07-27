from app.embeddings.models import Embedding
from app.vectorstore.factory import VectorStoreFactory
from app.vectorstore.models import SearchResult


class VectorStoreService:
    """Stores and searches embeddings in a collection."""

    @staticmethod
    def index_embeddings(embeddings: list[Embedding], collection: str = "") -> int:
        """Store the embeddings and return how many of them were written.

        Args:
            embeddings: What to store. An empty list writes nothing.
            collection: Where to store it. Empty means the shared collection.
        """
        if not embeddings:
            return 0

        store = VectorStoreFactory.create(collection)
        store.create_collection(len(embeddings[0].vector))
        store.upsert(embeddings)

        return len(embeddings)

    @staticmethod
    def search(
        vector: list[float],
        limit: int = 5,
        collection: str = "",
    ) -> list[SearchResult]:
        """Return the closest chunks of a collection to the query vector."""
        return VectorStoreFactory.create(collection).search(vector, limit)
