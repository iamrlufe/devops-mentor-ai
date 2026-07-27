from typing import Any

from psycopg.types.json import Jsonb

from app.database.connection import connection

COLUMNS = (
    "organization_id, name, slug, plan, is_active, metadata, "
    "created_at, updated_at"
)

UPSERT = f"""
INSERT INTO organizations ({COLUMNS})
VALUES (
    %(organization_id)s, %(name)s, %(slug)s, %(plan)s, %(is_active)s,
    %(metadata)s, %(created_at)s, %(updated_at)s
)
ON CONFLICT (organization_id) DO UPDATE SET
    name = EXCLUDED.name,
    slug = EXCLUDED.slug,
    plan = EXCLUDED.plan,
    is_active = EXCLUDED.is_active,
    metadata = EXCLUDED.metadata,
    updated_at = EXCLUDED.updated_at
"""


class OrganizationRepository:
    """Every SQL statement about organizations."""

    @staticmethod
    def get(organization_id: str) -> dict[str, Any] | None:
        """Return the row of an organization, or `None`."""
        with connection() as database:
            return database.execute(
                f"SELECT {COLUMNS} FROM organizations WHERE organization_id = %s",
                (organization_id,),
            ).fetchone()

    @staticmethod
    def upsert(values: dict[str, Any]) -> None:
        """Insert an organization, or replace the one with the same id."""
        payload = dict(values)
        payload["metadata"] = Jsonb(payload.get("metadata") or {})

        with connection() as database:
            database.execute(UPSERT, payload)

    @staticmethod
    def list() -> list[dict[str, Any]]:
        """Return every organization, oldest first."""
        with connection() as database:
            return database.execute(
                f"SELECT {COLUMNS} FROM organizations ORDER BY created_at"
            ).fetchall()

    @staticmethod
    def delete(organization_id: str) -> None:
        """Remove an organization. Missing ids are ignored."""
        with connection() as database:
            database.execute(
                "DELETE FROM organizations WHERE organization_id = %s",
                (organization_id,),
            )
