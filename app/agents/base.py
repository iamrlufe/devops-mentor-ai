from abc import ABC, abstractmethod
from typing import ClassVar

DEFAULT_CHAT_ID = "default"


class BaseAgent(ABC):
    """An assistant that answers a question in the context of a chat.

    An agent is described declaratively. Its identity, its prompt and the stack
    it runs on are class attributes, so changing which model, memory, retriever
    or collection an agent uses never touches a line of its logic. An empty
    value means "use what the platform is configured with".
    """

    # --- identity -----------------------------------------------------------

    #: Name the agent is registered and selected by, for example "teacher".
    name: ClassVar[str] = ""

    #: Short human readable description, shown by `GET /agents`.
    description: ClassVar[str] = ""

    #: Version of the agent definition, independent of the platform version.
    version: ClassVar[str] = "1.0.0"

    #: Who maintains this agent.
    author: ClassVar[str] = ""

    #: Free form labels for search and grouping, for example ("windows",).
    tags: ClassVar[tuple[str, ...]] = ()

    #: What the agent is good at, for example "docker", "database".
    #: A future coordinator uses it to route a question to the right agent.
    capabilities: ClassVar[tuple[str, ...]] = ()

    # --- the stack the agent runs on ----------------------------------------

    #: Name of the prompt in the `PromptRegistry`.
    prompt: ClassVar[str] = ""

    #: Overrides of the configured defaults, empty means "follow the settings".
    default_provider: ClassVar[str] = ""
    default_embedding: ClassVar[str] = ""
    default_memory: ClassVar[str] = ""
    default_retriever: ClassVar[str] = ""

    #: Collection this agent searches. Empty means the shared collection, so
    #: agents stay on one index unless they declare their own.
    collection: ClassVar[str] = ""

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

    @classmethod
    def metadata(cls) -> dict[str, object]:
        """Return the declared description of the agent, for `GET /agents`."""
        return {
            "name": cls.name,
            "description": cls.description,
            "version": cls.version,
            "author": cls.author,
            "tags": list(cls.tags),
            "capabilities": list(cls.capabilities),
            "prompt": cls.prompt,
            "provider": cls.default_provider,
            "embedding": cls.default_embedding,
            "memory": cls.default_memory,
            "retriever": cls.default_retriever,
            "collection": cls.collection,
        }
