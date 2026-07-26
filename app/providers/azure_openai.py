from typing import ClassVar

from app.config import settings
from app.models.chat_message import ChatMessage
from app.providers.base import NOT_IMPLEMENTED_MESSAGE, BaseProvider
from app.providers.registry import ProviderRegistry


@ProviderRegistry.register("azure_openai")
class AzureOpenAIProvider(BaseProvider):
    """Azure OpenAI. Addressed by endpoint and deployment instead of a model id.

    The configuration is wired and the provider is selectable, but the request
    to the API is not implemented yet.
    """

    capabilities: ClassVar[tuple[str, ...]] = ("chat", "vision", "embedding")

    def __init__(self) -> None:
        self.api_key = settings.azure_openai_api_key
        self.endpoint = settings.azure_openai_endpoint
        self.deployment = settings.azure_openai_deployment
        self.api_version = settings.azure_openai_api_version

    def generate(self, messages: list[ChatMessage]) -> str:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(
            NOT_IMPLEMENTED_MESSAGE.format(
                provider="Azure OpenAI",
                cls=type(self).__name__,
            )
        )
