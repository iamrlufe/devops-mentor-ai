from typing import ClassVar

from app.config import settings
from app.models.chat_message import ChatMessage
from app.providers.base import NOT_IMPLEMENTED_MESSAGE, BaseProvider
from app.providers.registry import ProviderRegistry


@ProviderRegistry.register("openrouter")
class OpenRouterProvider(BaseProvider):
    """OpenRouter, a gateway to many models behind one OpenAI-compatible API.

    The configuration is wired and the provider is selectable, but the request
    to the API is not implemented yet.
    """

    capabilities: ClassVar[tuple[str, ...]] = ("chat", "reasoning", "tool_calling")
    implemented: ClassVar[bool] = False
    supports_stream: ClassVar[bool] = True
    supports_tools: ClassVar[bool] = True
    supports_vision: ClassVar[bool] = True
    supports_function_calling: ClassVar[bool] = True
    supports_json: ClassVar[bool] = True
    context_window: ClassVar[int] = 128000

    def __init__(self) -> None:
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model

    def generate(self, messages: list[ChatMessage]) -> str:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(
            NOT_IMPLEMENTED_MESSAGE.format(
                provider="OpenRouter",
                cls=type(self).__name__,
            )
        )
