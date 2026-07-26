from abc import ABC, abstractmethod
from typing import ClassVar


class EmbeddingProvider(ABC):

    #: What the provider can do, for example "text", "local".
    capabilities: ClassVar[tuple[str, ...]] = ()

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts that are going to be stored, one vector per text."""
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        """Embed a search query. Providers that tell queries and documents apart
        override this method."""
        return self.embed([text])[0]
