from app.rag.base import Retriever
from app.rag.models import Document
from app.rag.registry import RetrieverRegistry

NOT_IMPLEMENTED = (
    "The Chroma retriever is registered but not implemented yet. "
    "Set RETRIEVER_PROVIDER to an implemented one, or implement "
    "ChromaRetriever.search()."
)


@RetrieverRegistry.register("chroma")
class ChromaRetriever(Retriever):
    """Semantic search over Chroma.

    Registered and selectable; the search is not implemented yet.
    """

    def search(self, query: str, limit: int = 5) -> list[Document]:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)
