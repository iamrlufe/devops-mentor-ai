from typing import Any

from app.conversations.base import ConversationStore
from app.conversations.models import Conversation, ConversationMessage
from app.conversations.registry import ConversationRegistry
from app.database.repositories.conversation_repository import ConversationRepository


def to_conversation(row: dict[str, Any]) -> Conversation:
    """Turn a database row into a conversation."""
    return Conversation(
        conversation_id=row["conversation_id"],
        organization_id=row["organization_id"],
        user_id=row["user_id"],
        chat_id=row["chat_id"],
        agent=row["agent"],
        provider=row["provider"],
        title=row["title"],
        message_count=row["message_count"],
        metadata=dict(row["metadata"] or {}),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def to_message(row: dict[str, Any]) -> ConversationMessage:
    """Turn a database row into a message."""
    return ConversationMessage(
        message_id=row["message_id"],
        conversation_id=row["conversation_id"],
        organization_id=row["organization_id"],
        user_id=row["user_id"],
        agent=row["agent"],
        provider=row["provider"],
        role=row["role"],
        message=row["message"],
        tokens=row["tokens"],
        metadata=dict(row["metadata"] or {}),
        created_at=row["created_at"],
    )


@ConversationRegistry.register("postgres")
class PostgresConversationStore(ConversationStore):
    """Keeps the history in PostgreSQL. This is the durable source of truth."""

    def get(self, conversation_id: str) -> Conversation | None:
        row = ConversationRepository.get(conversation_id)

        return to_conversation(row) if row else None

    def find(self, chat_id: str, agent: str) -> Conversation | None:
        row = ConversationRepository.find(chat_id, agent)

        return to_conversation(row) if row else None

    def save(self, conversation: Conversation) -> None:
        ConversationRepository.upsert(
            {
                "conversation_id": conversation.conversation_id,
                "organization_id": conversation.organization_id,
                "user_id": conversation.user_id,
                "chat_id": conversation.chat_id,
                "agent": conversation.agent,
                "provider": conversation.provider,
                "title": conversation.title,
                "message_count": conversation.message_count,
                "metadata": conversation.metadata,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
            }
        )

    def add_message(self, message: ConversationMessage) -> ConversationMessage:
        row = ConversationRepository.add_message(
            {
                "conversation_id": message.conversation_id,
                "organization_id": message.organization_id,
                "user_id": message.user_id,
                "agent": message.agent,
                "provider": message.provider,
                "role": message.role,
                "message": message.message,
                "tokens": message.tokens,
                "metadata": message.metadata,
            }
        )

        return ConversationMessage(
            message_id=row["message_id"],
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            agent=message.agent,
            provider=message.provider,
            role=message.role,
            message=message.message,
            tokens=message.tokens,
            metadata=message.metadata,
            created_at=row["created_at"],
        )

    def messages(
        self,
        conversation_id: str,
        limit: int = 0,
    ) -> list[ConversationMessage]:
        return [
            to_message(row)
            for row in ConversationRepository.messages(conversation_id, limit)
        ]

    def list_for_user(self, user_id: str) -> list[Conversation]:
        return [
            to_conversation(row)
            for row in ConversationRepository.list_for_user(user_id)
        ]

    def delete(self, conversation_id: str) -> None:
        ConversationRepository.delete(conversation_id)
