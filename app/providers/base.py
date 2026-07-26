from abc import ABC, abstractmethod

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
