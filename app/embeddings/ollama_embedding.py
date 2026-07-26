from typing import ClassVar

from app.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.registry import EmbeddingRegistry

NOT_IMPLEMENTED = (
    "The Ollama embedding provider is registered but not implemented yet. "
    "Set EMBEDDING_PROVIDER to an implemented one, or implement "
    "OllamaEmbeddingProvider.embed()."
)


@EmbeddingRegistry.register("ollama")
class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama embeddings.

    Registered and selectable; the request to the API is not implemented yet.
    """

    capabilities: ClassVar[tuple[str, ...]] = ("text", "local")

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)
