from typing import Any

from app.database.connection import connection

COLUMNS = (
    "chat_id, organization_id, user_id, agent, provider, embedding, "
    "memory, retriever, collection, prompt, created_at, updated_at"
)

UPSERT = f"""
INSERT INTO workspaces ({COLUMNS})
VALUES (
    %(chat_id)s, %(organization_id)s, %(user_id)s, %(agent)s, %(provider)s,
    %(embedding)s,
    %(memory)s, %(retriever)s, %(collection)s, %(prompt)s, %(created_at)s,
    %(updated_at)s
)
ON CONFLICT (chat_id) DO UPDATE SET
    organization_id = EXCLUDED.organization_id,
    user_id = EXCLUDED.user_id,
    agent = EXCLUDED.agent,
    provider = EXCLUDED.provider,
    embedding = EXCLUDED.embedding,
    memory = EXCLUDED.memory,
    retriever = EXCLUDED.retriever,
    collection = EXCLUDED.collection,
    prompt = EXCLUDED.prompt,
    updated_at = EXCLUDED.updated_at
"""


class WorkspaceRepository:
    """Every SQL statement about workspaces."""

    @staticmethod
    def get(chat_id: str) -> dict[str, Any] | None:
        """Return the row of a workspace, or `None`."""
        with connection() as database:
            return database.execute(
                f"SELECT {COLUMNS} FROM workspaces WHERE chat_id = %s",
                (chat_id,),
            ).fetchone()

    @staticmethod
    def upsert(values: dict[str, Any]) -> None:
        """Insert a workspace, or replace the one with the same chat id."""
        with connection() as database:
            database.execute(UPSERT, values)

    @staticmethod
    def list() -> list[dict[str, Any]]:
        """Return every workspace, by chat id."""
        with connection() as database:
            return database.execute(
                f"SELECT {COLUMNS} FROM workspaces ORDER BY chat_id"
            ).fetchall()

    @staticmethod
    def delete(chat_id: str) -> None:
        """Remove a workspace. Missing chats are ignored."""
        with connection() as database:
            database.execute("DELETE FROM workspaces WHERE chat_id = %s", (chat_id,))
