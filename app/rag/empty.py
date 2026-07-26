from app.rag.base import Retriever


class EmptyRetriever(Retriever):
    """Placeholder retriever. It finds nothing until a real vector store is wired in."""

    def search(self, query: str, limit: int = 5) -> list[str]:
        return []
