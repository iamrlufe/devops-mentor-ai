from typing import ClassVar

from app.config import settings
from app.models.chat_message import ChatMessage
from app.providers.base import NOT_IMPLEMENTED_MESSAGE, BaseProvider
from app.providers.registry import ProviderRegistry


@ProviderRegistry.register("claude")
class ClaudeProvider(BaseProvider):
    """Anthropic Claude through the Messages API.

    The configuration is wired and the provider is selectable, but the request
    to the API is not implemented yet.
    """

    capabilities: ClassVar[tuple[str, ...]] = ("chat", "reasoning", "files")
    implemented: ClassVar[bool] = False
    supports_stream: ClassVar[bool] = True
    supports_tools: ClassVar[bool] = True
    supports_vision: ClassVar[bool] = True
    supports_function_calling: ClassVar[bool] = True
    supports_json: ClassVar[bool] = True
    context_window: ClassVar[int] = 200000

    def __init__(self) -> None:
        self.api_key = settings.claude_api_key
        self.model = settings.claude_model

    def generate(self, messages: list[ChatMessage]) -> str:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(
            NOT_IMPLEMENTED_MESSAGE.format(
                provider="Claude",
                cls=type(self).__name__,
            )
        )
