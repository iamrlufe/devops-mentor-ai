from app.rag.base import Retriever
from app.rag.qdrant_retriever import QdrantRetriever


class RetrieverFactory:
    _retriever: Retriever | None = None

    @staticmethod
    def create() -> Retriever:
        """Return the retriever shared by the whole process."""
        if RetrieverFactory._retriever is None:
            RetrieverFactory._retriever = QdrantRetriever()

        return RetrieverFactory._retriever
