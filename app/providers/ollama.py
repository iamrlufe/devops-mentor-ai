from typing import ClassVar

from app.config import settings
from app.models.chat_message import ChatMessage
from app.providers.base import NOT_IMPLEMENTED_MESSAGE, BaseProvider
from app.providers.registry import ProviderRegistry


@ProviderRegistry.register("ollama")
class OllamaProvider(BaseProvider):
    """Ollama, a local model runtime. Needs a base URL instead of an API key.

    The configuration is wired and the provider is selectable, but the request
    to the runtime is not implemented yet.
    """

    capabilities: ClassVar[tuple[str, ...]] = ("chat", "local", "embedding")
    implemented: ClassVar[bool] = False
    supports_stream: ClassVar[bool] = True
    supports_tools: ClassVar[bool] = True
    supports_vision: ClassVar[bool] = False
    supports_function_calling: ClassVar[bool] = True
    supports_json: ClassVar[bool] = True
    context_window: ClassVar[int] = 8192

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    def generate(self, messages: list[ChatMessage]) -> str:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(
            NOT_IMPLEMENTED_MESSAGE.format(
                provider="Ollama",
                cls=type(self).__name__,
            )
        )
