from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts that are going to be stored, one vector per text."""
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        """Embed a search query. Providers that tell queries and documents apart
        override this method."""
        return self.embed([text])[0]
