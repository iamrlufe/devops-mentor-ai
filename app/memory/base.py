from abc import ABC, abstractmethod

from app.memory.models import Message


class MemoryProvider(ABC):

    @abstractmethod
    def load(self, chat_id: str) -> list[Message]:
        """Return the conversation history of a chat, oldest message first."""
        raise NotImplementedError

    @abstractmethod
    def save(self, chat_id: str, role: str, text: str) -> None:
        """Append a message to the conversation history of a chat."""
        raise NotImplementedError

    @abstractmethod
    def clear(self, chat_id: str) -> None:
        """Drop the whole conversation history of a chat."""
        raise NotImplementedError
