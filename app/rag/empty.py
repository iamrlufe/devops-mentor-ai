from app.rag.base import Retriever
from app.rag.models import Document
from app.rag.registry import RetrieverRegistry


@RetrieverRegistry.register("empty")
class EmptyRetriever(Retriever):
    """Finds nothing. Useful to run the mentor without a document index."""

    def search(self, query: str, limit: int = 5) -> list[Document]:
        return []
