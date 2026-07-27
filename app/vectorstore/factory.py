from app.config import settings
from app.vectorstore.base import VectorStore
from app.vectorstore.qdrant_store import QdrantVectorStore


class VectorStoreFactory:
    """Builds a vector store for a collection.

    One instance is kept per collection, so an agent with its own collection
    reuses a client instead of opening a new one on every request.
    """

    _instances: dict[str, VectorStore] = {}

    @staticmethod
    def create(collection: str = "") -> VectorStore:
        """Return the vector store of a collection.

        Args:
            collection: Name of the collection. Empty means the shared one from
                `QDRANT_COLLECTION`.
        """
        name = collection or settings.qdrant_collection

        if name not in VectorStoreFactory._instances:
            VectorStoreFactory._instances[name] = QdrantVectorStore(name)

        return VectorStoreFactory._instances[name]
