import threading
from typing import ClassVar

from app.config import settings
from app.core.instances import get_or_create
from app.vectorstore.base import VectorStore
from app.vectorstore.qdrant_store import QdrantVectorStore


class VectorStoreFactory:
    """Builds a vector store for a collection.

    One instance is kept per collection, so an agent with its own collection
    reuses a client instead of opening a new one on every request.
    """

    _instances: ClassVar[dict[str, VectorStore]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(collection: str = "") -> VectorStore:
        """Return the vector store of a collection.

        Args:
            collection: Name of the collection. Empty means the shared one from
                `QDRANT_COLLECTION`.
        """
        name = collection or settings.qdrant_collection

        return get_or_create(
            VectorStoreFactory._instances,
            VectorStoreFactory._lock,
            name,
            lambda: QdrantVectorStore(name),
        )
