from typing import ClassVar

from app.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.registry import EmbeddingRegistry

NOT_IMPLEMENTED = (
    "The Jina embedding provider is registered but not implemented yet. "
    "Set EMBEDDING_PROVIDER to an implemented one, or implement "
    "JinaEmbeddingProvider.embed()."
)


@EmbeddingRegistry.register("jina")
class JinaEmbeddingProvider(EmbeddingProvider):
    """Jina embeddings.

    Registered and selectable; the request to the API is not implemented yet.
    """

    capabilities: ClassVar[tuple[str, ...]] = ("text", "multilingual")

    def __init__(self) -> None:
        self.api_key = settings.jina_api_key

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)
