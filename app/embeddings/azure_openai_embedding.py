from typing import ClassVar

from app.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.registry import EmbeddingRegistry

NOT_IMPLEMENTED = (
    "The Azure OpenAI embedding provider is registered but not implemented "
    "yet. Set EMBEDDING_PROVIDER to an implemented one, or implement "
    "AzureOpenAIEmbeddingProvider.embed()."
)


@EmbeddingRegistry.register("azure_openai")
class AzureOpenAIEmbeddingProvider(EmbeddingProvider):
    """Azure OpenAI embeddings, addressed by endpoint and deployment.

    Registered and selectable; the request to the API is not implemented yet.
    """

    capabilities: ClassVar[tuple[str, ...]] = ("text",)

    def __init__(self) -> None:
        self.api_key = settings.azure_openai_api_key
        self.endpoint = settings.azure_openai_endpoint
        self.deployment = settings.azure_openai_deployment
        self.api_version = settings.azure_openai_api_version

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)
