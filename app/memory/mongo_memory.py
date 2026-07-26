from app.memory.base import MemoryProvider
from app.memory.models import Message
from app.memory.registry import MemoryRegistry

NOT_IMPLEMENTED = (
    "The MongoDB memory provider is registered but not implemented yet. "
    "Set MEMORY_PROVIDER to an implemented one, or implement MongoMemoryProvider."
)


@MemoryRegistry.register("mongo")
class MongoMemoryProvider(MemoryProvider):
    """Conversation history in MongoDB.

    Registered and selectable; the storage is not implemented yet.
    """

    def load(self, chat_id: str) -> list[Message]:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)

    def save(self, chat_id: str, role: str, text: str) -> None:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)

    def clear(self, chat_id: str) -> None:
        """Not implemented yet.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(NOT_IMPLEMENTED)
