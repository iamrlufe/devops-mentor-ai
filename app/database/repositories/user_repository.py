from typing import Any

from psycopg.types.json import Jsonb

from app.database.connection import connection

COLUMNS = (
    "user_id, telegram_id, name, phone, language, timezone, "
    "preferred_agent, preferred_provider, last_agent, last_provider, "
    "message_count, conversation_count, registration_source, metadata, "
    "created_at, updated_at, last_seen"
)

UPSERT = f"""
INSERT INTO users ({COLUMNS})
VALUES (
    %(user_id)s, %(telegram_id)s, %(name)s, %(phone)s, %(language)s,
    %(timezone)s, %(preferred_agent)s, %(preferred_provider)s, %(last_agent)s,
    %(last_provider)s, %(message_count)s, %(conversation_count)s,
    %(registration_source)s, %(metadata)s, %(created_at)s, %(updated_at)s,
    %(last_seen)s
)
ON CONFLICT (user_id) DO UPDATE SET
    telegram_id = EXCLUDED.telegram_id,
    name = EXCLUDED.name,
    phone = EXCLUDED.phone,
    language = EXCLUDED.language,
    timezone = EXCLUDED.timezone,
    preferred_agent = EXCLUDED.preferred_agent,
    preferred_provider = EXCLUDED.preferred_provider,
    last_agent = EXCLUDED.last_agent,
    last_provider = EXCLUDED.last_provider,
    message_count = EXCLUDED.message_count,
    conversation_count = EXCLUDED.conversation_count,
    registration_source = EXCLUDED.registration_source,
    metadata = EXCLUDED.metadata,
    updated_at = EXCLUDED.updated_at,
    last_seen = EXCLUDED.last_seen
"""


class UserRepository:
    """Every SQL statement about user profiles.

    The repository speaks rows and nothing else: it holds no rules about what a
    profile means, which keeps the SQL out of the store and the store out of the
    database.
    """

    @staticmethod
    def get(user_id: str) -> dict[str, Any] | None:
        """Return the row of a profile, or `None`."""
        with connection() as database:
            return database.execute(
                f"SELECT {COLUMNS} FROM users WHERE user_id = %s",
                (user_id,),
            ).fetchone()

    @staticmethod
    def get_by_telegram_id(telegram_id: str) -> dict[str, Any] | None:
        """Return the row linked to a Telegram account, or `None`."""
        with connection() as database:
            return database.execute(
                f"SELECT {COLUMNS} FROM users WHERE telegram_id = %s",
                (telegram_id,),
            ).fetchone()

    @staticmethod
    def upsert(values: dict[str, Any]) -> None:
        """Insert a profile, or replace the one with the same user id."""
        payload = dict(values)
        payload["metadata"] = Jsonb(payload.get("metadata") or {})

        with connection() as database:
            database.execute(UPSERT, payload)

    @staticmethod
    def list() -> list[dict[str, Any]]:
        """Return every profile, oldest first."""
        with connection() as database:
            return database.execute(
                f"SELECT {COLUMNS} FROM users ORDER BY created_at, user_id"
            ).fetchall()

    @staticmethod
    def delete(user_id: str) -> None:
        """Remove a profile. Missing ids are ignored."""
        with connection() as database:
            database.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
