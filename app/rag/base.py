from abc import ABC, abstractmethod


class Retriever(ABC):

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[str]:
        """Return up to `limit` document texts relevant to the query."""
        raise NotImplementedError
