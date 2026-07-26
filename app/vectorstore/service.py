from app.embeddings.models import Embedding
from app.vectorstore.factory import VectorStoreFactory
from app.vectorstore.models import SearchResult


class VectorStoreService:

    @staticmethod
    def index_embeddings(embeddings: list[Embedding]) -> int:
        """Store the embeddings and return how many of them were written."""
        if not embeddings:
            return 0

        store = VectorStoreFactory.create()
        store.create_collection(len(embeddings[0].vector))
        store.upsert(embeddings)

        return len(embeddings)

    @staticmethod
    def search(vector: list[float], limit: int = 5) -> list[SearchResult]:
        return VectorStoreFactory.create().search(vector, limit)
