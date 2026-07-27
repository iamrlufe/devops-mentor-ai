from typing import Any

from app.database.connection import connection


class MemoryRepository:
    """Every SQL statement about the conversation memory.

    Memory is the short window the prompt builder reads. The conversation tables
    keep the full history, so trimming here never loses anything.
    """

    @staticmethod
    def load(chat_key: str, limit: int = 0) -> list[dict[str, Any]]:
        """Return the stored messages of a key, oldest first."""
        with connection() as database:
            if limit <= 0:
                return database.execute(
                    "SELECT role, content FROM memory_messages "
                    "WHERE chat_key = %s ORDER BY message_id",
                    (chat_key,),
                ).fetchall()

            rows = database.execute(
                "SELECT role, content FROM memory_messages "
                "WHERE chat_key = %s ORDER BY message_id DESC LIMIT %s",
                (chat_key, limit),
            ).fetchall()

        return list(reversed(rows))

    @staticmethod
    def save(chat_key: str, role: str, content: str, limit: int = 0) -> None:
        """Append a message and drop everything older than the limit.

        Args:
            chat_key: Which history to append to.
            role: Who produced the message.
            content: What was said.
            limit: How many messages to keep. 0 keeps everything.
        """
        with connection() as database, database.transaction():
            database.execute(
                "INSERT INTO memory_messages (chat_key, role, content) "
                "VALUES (%s, %s, %s)",
                (chat_key, role, content),
            )

            if limit > 0:
                database.execute(
                    "DELETE FROM memory_messages WHERE chat_key = %s AND message_id "
                    "NOT IN (SELECT message_id FROM memory_messages "
                    "WHERE chat_key = %s ORDER BY message_id DESC LIMIT %s)",
                    (chat_key, chat_key, limit),
                )

    @staticmethod
    def clear(chat_key: str) -> None:
        """Drop the stored memory of a key."""
        with connection() as database:
            database.execute(
                "DELETE FROM memory_messages WHERE chat_key = %s", (chat_key,)
            )
