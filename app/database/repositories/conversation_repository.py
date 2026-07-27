from typing import Any

from psycopg.types.json import Jsonb

from app.database.connection import connection

CONVERSATION_COLUMNS = (
    "conversation_id, user_id, chat_id, agent, provider, title, "
    "message_count, metadata, created_at, updated_at"
)
MESSAGE_COLUMNS = (
    "message_id, conversation_id, user_id, agent, provider, role, message, "
    "tokens, metadata, created_at"
)

UPSERT_CONVERSATION = f"""
INSERT INTO conversations ({CONVERSATION_COLUMNS})
VALUES (
    %(conversation_id)s, %(user_id)s, %(chat_id)s, %(agent)s, %(provider)s,
    %(title)s, %(message_count)s, %(metadata)s, %(created_at)s, %(updated_at)s
)
ON CONFLICT (conversation_id) DO UPDATE SET
    user_id = EXCLUDED.user_id,
    chat_id = EXCLUDED.chat_id,
    agent = EXCLUDED.agent,
    provider = EXCLUDED.provider,
    title = EXCLUDED.title,
    message_count = EXCLUDED.message_count,
    metadata = EXCLUDED.metadata,
    updated_at = EXCLUDED.updated_at
"""

INSERT_MESSAGE = """
INSERT INTO conversation_messages (
    conversation_id, user_id, agent, provider, role, message, tokens, metadata
)
VALUES (
    %(conversation_id)s, %(user_id)s, %(agent)s, %(provider)s, %(role)s,
    %(message)s, %(tokens)s, %(metadata)s
)
RETURNING message_id, created_at
"""


class ConversationRepository:
    """Every SQL statement about conversations and their messages."""

    @staticmethod
    def get(conversation_id: str) -> dict[str, Any] | None:
        """Return the row of a conversation, or `None`."""
        with connection() as database:
            return database.execute(
                f"SELECT {CONVERSATION_COLUMNS} FROM conversations "
                "WHERE conversation_id = %s",
                (conversation_id,),
            ).fetchone()

    @staticmethod
    def find(chat_id: str, agent: str) -> dict[str, Any] | None:
        """Return the newest conversation of a chat with an agent, or `None`."""
        with connection() as database:
            return database.execute(
                f"SELECT {CONVERSATION_COLUMNS} FROM conversations "
                "WHERE chat_id = %s AND agent = %s "
                "ORDER BY created_at DESC LIMIT 1",
                (chat_id, agent),
            ).fetchone()

    @staticmethod
    def upsert(values: dict[str, Any]) -> None:
        """Insert a conversation, or replace the one with the same id."""
        payload = dict(values)
        payload["metadata"] = Jsonb(payload.get("metadata") or {})

        with connection() as database:
            database.execute(UPSERT_CONVERSATION, payload)

    @staticmethod
    def list_for_user(user_id: str) -> list[dict[str, Any]]:
        """Return the conversations of a user, newest first."""
        with connection() as database:
            return database.execute(
                f"SELECT {CONVERSATION_COLUMNS} FROM conversations "
                "WHERE user_id = %s ORDER BY updated_at DESC",
                (user_id,),
            ).fetchall()

    @staticmethod
    def add_message(values: dict[str, Any]) -> dict[str, Any]:
        """Append a message and bump the counters of its conversation.

        The message and the counter move together, so a reader never sees a
        conversation whose count disagrees with its messages.
        """
        payload = dict(values)
        payload["metadata"] = Jsonb(payload.get("metadata") or {})

        with connection() as database, database.transaction():
            row = database.execute(INSERT_MESSAGE, payload).fetchone()
            database.execute(
                "UPDATE conversations SET message_count = message_count + 1, "
                "updated_at = now() WHERE conversation_id = %s",
                (payload["conversation_id"],),
            )

        return row

    @staticmethod
    def messages(conversation_id: str, limit: int = 0) -> list[dict[str, Any]]:
        """Return the messages of a conversation, oldest first.

        Args:
            conversation_id: Which conversation to read.
            limit: How many of the newest messages to return. 0 means all of
                them, still in chronological order.
        """
        with connection() as database:
            if limit <= 0:
                return database.execute(
                    f"SELECT {MESSAGE_COLUMNS} FROM conversation_messages "
                    "WHERE conversation_id = %s ORDER BY message_id",
                    (conversation_id,),
                ).fetchall()

            rows = database.execute(
                f"SELECT {MESSAGE_COLUMNS} FROM conversation_messages "
                "WHERE conversation_id = %s ORDER BY message_id DESC LIMIT %s",
                (conversation_id, limit),
            ).fetchall()

        return list(reversed(rows))

    @staticmethod
    def delete(conversation_id: str) -> None:
        """Remove a conversation with its messages."""
        with connection() as database:
            database.execute(
                "DELETE FROM conversations WHERE conversation_id = %s",
                (conversation_id,),
            )
