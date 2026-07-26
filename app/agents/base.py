from abc import ABC, abstractmethod
from typing import ClassVar

DEFAULT_CHAT_ID = "default"


class BaseAgent(ABC):
    """An assistant that answers a question in the context of a chat.

    An agent owns its system prompt and its capabilities; everything it needs
    to work — the model, the memory, the retriever — is resolved through
    factories, so the agent depends on interfaces and never on a concrete
    implementation.
    """

    #: Name the agent is registered and selected by, for example "teacher".
    name: ClassVar[str] = ""

    #: Short human readable description, shown by `GET /agents`.
    description: ClassVar[str] = ""

    #: What the agent is good at, for example "docker", "database".
    #: A future coordinator uses it to route a question to the right agent.
    capabilities: ClassVar[tuple[str, ...]] = ()

    @abstractmethod
    def ask(self, prompt: str, chat_id: str = DEFAULT_CHAT_ID) -> str:
        """Answer a question and remember the exchange.

        Args:
            prompt: The question of the user.
            chat_id: The conversation the question belongs to.

        Returns:
            The answer of the model.
        """
        raise NotImplementedError
