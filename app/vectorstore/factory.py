from app.vectorstore.base import VectorStore
from app.vectorstore.qdrant_store import QdrantVectorStore


class VectorStoreFactory:
    _store: VectorStore | None = None

    @staticmethod
    def create() -> VectorStore:
        """Return the vector store shared by the whole process."""
        if VectorStoreFactory._store is None:
            VectorStoreFactory._store = QdrantVectorStore()

        return VectorStoreFactory._store
