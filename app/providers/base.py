from abc import ABC, abstractmethod
from typing import ClassVar

from app.models.chat_message import ChatMessage

NOT_IMPLEMENTED_MESSAGE = (
    "The {provider} provider is registered but not implemented yet. "
    "Set LLM_PROVIDER to a provider that is implemented, or implement "
    "{cls}.generate()."
)


class BaseProvider(ABC):
    """A large language model behind a provider-independent interface.

    Everything above this layer works with `ChatMessage` objects. Turning them
    into the wire format of a concrete API is the job of the implementation,
    so a new provider never changes the agent, the prompt builder or the memory.
    """

    #: What the provider can do, for example "chat", "vision", "reasoning".
    #: A future coordinator uses it to route a request to a capable provider.
    capabilities: ClassVar[tuple[str, ...]] = ()

    #: Whether `generate` really talks to the model. A registered provider that
    #: is not implemented yet is selectable and reports itself as such instead
    #: of failing with a traceback.
    implemented: ClassVar[bool] = False

    #: Declared feature support, reported by `GET /providers`.
    supports_stream: ClassVar[bool] = False
    supports_tools: ClassVar[bool] = False
    supports_vision: ClassVar[bool] = False
    supports_function_calling: ClassVar[bool] = False
    supports_json: ClassVar[bool] = False

    #: Context window of the configured model in tokens, 0 when unknown.
    context_window: ClassVar[int] = 0

    @classmethod
    def metadata(cls) -> dict[str, object]:
        """Return the declared description of the provider."""
        return {
            "name": cls.provider_name(),
            "implemented": cls.implemented,
            "supports_stream": cls.supports_stream,
            "supports_tools": cls.supports_tools,
            "supports_vision": cls.supports_vision,
            "supports_function_calling": cls.supports_function_calling,
            "supports_json": cls.supports_json,
            "context_window": cls.context_window,
            "capabilities": list(cls.capabilities),
        }

    @classmethod
    def provider_name(cls) -> str:
        """Return the name this provider is registered under."""
        from app.providers.registry import ProviderRegistry

        return ProviderRegistry.name_of(cls)

    @abstractmethod
    def generate(self, messages: list[ChatMessage]) -> str:
        """Return the answer of the model to the given conversation.

        Args:
            messages: The conversation, ordered from the system prompt to the
                current user message.

        Returns:
            The generated answer.

        Raises:
            RuntimeError: If the model could not be reached or returned nothing.
        """
        raise NotImplementedError
