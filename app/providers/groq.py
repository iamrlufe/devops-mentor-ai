from app.config import settings
from app.models.chat_message import ChatMessage
from app.providers.base import NOT_IMPLEMENTED_MESSAGE, BaseProvider
from app.providers.registry import ProviderRegistry


@ProviderRegistry.register("groq")
class GroqProvider(BaseProvider):
    """Groq, an OpenAI-compatible API on their own inference hardware.

    The configuration is wired and the provider is selectable, but the request
    to the API is not implemented yet.
    """

    def __init__(self) -> None:
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model

    def generate(self, messages: list[ChatMessage]) -> str:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(
            NOT_IMPLEMENTED_MESSAGE.format(
                provider="Groq",
                cls=type(self).__name__,
            )
        )
