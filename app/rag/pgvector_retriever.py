from app.rag.base import Retriever
from app.rag.models import Document
from app.rag.registry import RetrieverRegistry

NOT_IMPLEMENTED = (
    "The pgvector retriever is registered but not implemented yet. "
    "Set RETRIEVER_PROVIDER to an implemented one, or implement "
    "PgVectorRetriever.search()."
)


@RetrieverRegistry.register("pgvector")
class PgVectorRetriever(Retriever):
    """Semantic search over pgvector.

    Registered and selectable; the search is not implemented yet.
    """

    def search(self, query: str, limit: int = 5) -> list[Document]:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)
