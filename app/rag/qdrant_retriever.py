from app.embeddings.factory import EmbeddingFactory
from app.rag.base import Retriever
from app.rag.models import Document
from app.rag.registry import RetrieverRegistry
from app.vectorstore.models import SearchResult
from app.vectorstore.service import VectorStoreService

TEXT_KEY = "text"


@RetrieverRegistry.register("qdrant")
class QdrantRetriever(Retriever):
    """Searches the indexed chunks by the meaning of the query."""

    def search(self, query: str, limit: int = 5) -> list[Document]:
        if not query.strip():
            return []

        vector = EmbeddingFactory.create().embed_query(query)
        results = VectorStoreService.search(vector, limit)

        return [self._build_document(result) for result in results]

    @staticmethod
    def _build_document(result: SearchResult) -> Document:
        metadata = result.metadata or {}

        return Document(
            id=result.chunk_id,
            text=metadata.get(TEXT_KEY, ""),
            metadata=metadata,
            score=result.score,
        )
