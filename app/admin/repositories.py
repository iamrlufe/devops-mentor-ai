from typing import Any

from app.database.connection import connection


class AdminRepository:
    """Every aggregate SQL statement the administration reads.

    The administration asks questions the running platform never asks — counts,
    activity windows, per-agent usage — so those statements live here instead of
    leaking into the stores that serve requests.
    """

    @staticmethod
    def counters() -> dict[str, Any]:
        """Return the counts the dashboard is built from."""
        with connection() as database:
            return database.execute(
                """
                SELECT
                    (SELECT count(*) FROM users) AS users_total,
                    (SELECT count(*) FROM users
                     WHERE last_seen >= current_date) AS active_today,
                    (SELECT count(*) FROM users
                     WHERE last_seen >= now() - interval '7 days') AS active_week,
                    (SELECT count(*) FROM users
                     WHERE created_at >= current_date) AS registrations_today,
                    (SELECT count(*) FROM conversation_messages)
                        AS messages_total,
                    (SELECT count(*) FROM conversation_messages
                     WHERE created_at >= current_date) AS messages_today,
                    (SELECT count(*) FROM conversations) AS conversations_total,
                    (SELECT count(*) FROM workspaces) AS workspaces_total,
                    (SELECT count(*) FROM organizations) AS organizations_total
                """
            ).fetchone()

    @staticmethod
    def users(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Return profiles with their activity, newest first."""
        with connection() as database:
            return database.execute(
                "SELECT user_id, organization_id, telegram_id, name, language, "
                "timezone, registration_source, message_count, "
                "conversation_count, last_agent, last_provider, last_seen, "
                "created_at FROM users ORDER BY created_at DESC "
                "LIMIT %s OFFSET %s",
                (limit, offset),
            ).fetchall()

    @staticmethod
    def user_statistics(user_id: str) -> dict[str, Any]:
        """Return what one user has produced."""
        with connection() as database:
            return database.execute(
                """
                SELECT
                    (SELECT count(*) FROM conversations
                     WHERE user_id = %(user_id)s) AS conversations,
                    (SELECT count(*) FROM conversation_messages
                     WHERE user_id = %(user_id)s) AS messages,
                    (SELECT count(*) FROM request_metrics
                     WHERE user_id = %(user_id)s) AS requests,
                    (SELECT coalesce(round(avg(latency_ms) FILTER (
                        WHERE success)), 0) FROM request_metrics
                     WHERE user_id = %(user_id)s) AS average_latency_ms,
                    (SELECT coalesce(sum(tokens), 0) FROM conversation_messages
                     WHERE user_id = %(user_id)s) AS tokens
                """,
                {"user_id": user_id},
            ).fetchone()

    @staticmethod
    def user_memory(user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Return the memory windows of a user, newest message first.

        Memory is keyed by `agent:chat_id`, and the chat of a Telegram user is
        their user id, so the windows of one user are the keys ending with it.
        """
        with connection() as database:
            return database.execute(
                "SELECT chat_key, role, content, created_at "
                "FROM memory_messages WHERE chat_key LIKE %s "
                "ORDER BY message_id DESC LIMIT %s",
                (f"%:{user_id}", limit),
            ).fetchall()

    @staticmethod
    def conversations(
        user_id: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return conversations, newest first, optionally of one user."""
        with connection() as database:
            if user_id:
                return database.execute(
                    "SELECT conversation_id, organization_id, user_id, chat_id, "
                    "agent, provider, title, message_count, created_at, "
                    "updated_at FROM conversations WHERE user_id = %s "
                    "ORDER BY updated_at DESC LIMIT %s OFFSET %s",
                    (user_id, limit, offset),
                ).fetchall()

            return database.execute(
                "SELECT conversation_id, organization_id, user_id, chat_id, "
                "agent, provider, title, message_count, created_at, updated_at "
                "FROM conversations ORDER BY updated_at DESC LIMIT %s OFFSET %s",
                (limit, offset),
            ).fetchall()

    @staticmethod
    def messages(conversation_id: str, limit: int = 200) -> list[dict[str, Any]]:
        """Return the messages of a conversation, oldest first."""
        with connection() as database:
            return database.execute(
                "SELECT message_id, conversation_id, user_id, agent, provider, "
                "role, message, tokens, created_at FROM conversation_messages "
                "WHERE conversation_id = %s ORDER BY message_id LIMIT %s",
                (conversation_id, limit),
            ).fetchall()

    @staticmethod
    def user_history(user_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """Return the newest messages of a user across every conversation."""
        with connection() as database:
            rows = database.execute(
                "SELECT message_id, conversation_id, agent, provider, role, "
                "message, tokens, created_at FROM conversation_messages "
                "WHERE user_id = %s ORDER BY message_id DESC LIMIT %s",
                (user_id, limit),
            ).fetchall()

        return list(reversed(rows))

    @staticmethod
    def registrations(days: int = 7) -> list[dict[str, Any]]:
        """Return how many profiles were created per day."""
        with connection() as database:
            return database.execute(
                "SELECT date_trunc('day', created_at)::date AS day, "
                "count(*) AS registrations FROM users "
                "WHERE created_at >= current_date - %s::integer "
                "GROUP BY day ORDER BY day",
                (days,),
            ).fetchall()

    @staticmethod
    def messages_per_day(days: int = 7) -> list[dict[str, Any]]:
        """Return how many messages were stored per day."""
        with connection() as database:
            return database.execute(
                "SELECT date_trunc('day', created_at)::date AS day, "
                "count(*) AS messages FROM conversation_messages "
                "WHERE created_at >= current_date - %s::integer "
                "GROUP BY day ORDER BY day",
                (days,),
            ).fetchall()

    @staticmethod
    def workspace_selections(column: str) -> list[dict[str, Any]]:
        """Return how many workspaces pin each value of one column.

        Args:
            column: Which workspace selection to group by.

        Raises:
            ValueError: If the column is not a workspace selection.
        """
        allowed = {"agent", "provider", "embedding", "memory", "retriever"}

        if column not in allowed:
            raise ValueError(
                f"Unknown workspace column: '{column}'. "
                f"Known: {', '.join(sorted(allowed))}."
            )

        with connection() as database:
            return database.execute(
                f"SELECT {column} AS name, count(*) AS workspaces "  # noqa: S608
                f"FROM workspaces WHERE {column} <> '' "
                f"GROUP BY {column} ORDER BY workspaces DESC"
            ).fetchall()

    @staticmethod
    def agent_usage() -> list[dict[str, Any]]:
        """Return users and messages per agent, from the stored history."""
        with connection() as database:
            return database.execute(
                "SELECT agent, count(*) AS messages, "
                "count(DISTINCT user_id) FILTER (WHERE user_id <> '') AS users "
                "FROM conversation_messages WHERE agent <> '' "
                "GROUP BY agent ORDER BY messages DESC"
            ).fetchall()
