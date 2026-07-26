from typing import ClassVar

from app.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.registry import EmbeddingRegistry

NOT_IMPLEMENTED = (
    "The Voyage AI embedding provider is registered but not implemented yet. "
    "Set EMBEDDING_PROVIDER to an implemented one, or implement "
    "VoyageAIEmbeddingProvider.embed()."
)


@EmbeddingRegistry.register("voyageai")
class VoyageAIEmbeddingProvider(EmbeddingProvider):
    """Voyage AI embeddings.

    Registered and selectable; the request to the API is not implemented yet.
    """

    capabilities: ClassVar[tuple[str, ...]] = ("text", "reranking")

    def __init__(self) -> None:
        self.api_key = settings.voyageai_api_key

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)
