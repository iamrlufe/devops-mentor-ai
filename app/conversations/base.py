from abc import ABC, abstractmethod

from app.conversations.models import Conversation, ConversationMessage


class ConversationStore(ABC):
    """Where the conversation history lives.

    This is the source of truth of what was said. A new backend is a new class
    registered under a new name, with nothing else to change.
    """

    @abstractmethod
    def get(self, conversation_id: str) -> Conversation | None:
        """Return a conversation by id, or `None`."""
        raise NotImplementedError

    @abstractmethod
    def find(self, chat_id: str, agent: str) -> Conversation | None:
        """Return the newest conversation of a chat with an agent, or `None`."""
        raise NotImplementedError

    @abstractmethod
    def save(self, conversation: Conversation) -> None:
        """Store a conversation, replacing the one with the same id."""
        raise NotImplementedError

    @abstractmethod
    def add_message(self, message: ConversationMessage) -> ConversationMessage:
        """Append a message and return it as stored."""
        raise NotImplementedError

    @abstractmethod
    def messages(
        self,
        conversation_id: str,
        limit: int = 0,
    ) -> list[ConversationMessage]:
        """Return the messages of a conversation, oldest first."""
        raise NotImplementedError

    @abstractmethod
    def list_for_user(self, user_id: str) -> list[Conversation]:
        """Return the conversations of a user, newest first."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, conversation_id: str) -> None:
        """Remove a conversation with its messages."""
        raise NotImplementedError
