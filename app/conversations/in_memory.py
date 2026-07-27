import threading
from dataclasses import replace

from app.conversations.base import ConversationStore
from app.conversations.models import Conversation, ConversationMessage
from app.conversations.registry import ConversationRegistry


@ConversationRegistry.register("in_memory")
class InMemoryConversationStore(ConversationStore):
    """Demo store: keeps the history in the process memory.

    It is lost on restart. `PostgresConversationStore` is what a running
    deployment uses.
    """

    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._messages: dict[str, list[ConversationMessage]] = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def get(self, conversation_id: str) -> Conversation | None:
        with self._lock:
            return self._conversations.get(conversation_id)

    def find(self, chat_id: str, agent: str) -> Conversation | None:
        with self._lock:
            found = [
                conversation
                for conversation in self._conversations.values()
                if conversation.chat_id == chat_id and conversation.agent == agent
            ]

        return max(found, key=lambda item: item.created_at) if found else None

    def save(self, conversation: Conversation) -> None:
        with self._lock:
            self._conversations[conversation.conversation_id] = conversation
            self._messages.setdefault(conversation.conversation_id, [])

    def add_message(self, message: ConversationMessage) -> ConversationMessage:
        with self._lock:
            stored = replace(message, message_id=self._next_id)
            self._next_id += 1
            self._messages.setdefault(message.conversation_id, []).append(stored)

            conversation = self._conversations.get(message.conversation_id)

            if conversation is not None:
                self._conversations[message.conversation_id] = (
                    conversation.with_changes(
                        message_count=conversation.message_count + 1
                    )
                )

        return stored

    def messages(
        self,
        conversation_id: str,
        limit: int = 0,
    ) -> list[ConversationMessage]:
        with self._lock:
            stored = list(self._messages.get(conversation_id, []))

        return stored[-limit:] if limit > 0 else stored

    def list_for_user(self, user_id: str) -> list[Conversation]:
        with self._lock:
            found = [
                conversation
                for conversation in self._conversations.values()
                if conversation.user_id == user_id
            ]

        return sorted(found, key=lambda item: item.updated_at, reverse=True)

    def delete(self, conversation_id: str) -> None:
        with self._lock:
            self._conversations.pop(conversation_id, None)
            self._messages.pop(conversation_id, None)
