from pathlib import Path

from app.database.connection import connection

MIGRATIONS_DIRECTORY = Path(__file__).resolve().parents[2] / "migrations"
MIGRATION_SUFFIX = ".sql"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    name       TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


class MigrationRunner:
    """Applies the plain SQL files of `migrations/` once each, in name order."""

    @staticmethod
    def pending() -> list[Path]:
        """Return the migrations that have not been applied yet."""
        applied = MigrationRunner.applied()

        return [
            path
            for path in sorted(MIGRATIONS_DIRECTORY.glob(f"*{MIGRATION_SUFFIX}"))
            if path.name not in applied
        ]

    @staticmethod
    def applied() -> set[str]:
        """Return the names of the migrations already recorded."""
        with connection() as database:
            database.execute(CREATE_TABLE)
            rows = database.execute("SELECT name FROM schema_migrations").fetchall()

        return {row["name"] for row in rows}

    @staticmethod
    def run() -> list[str]:
        """Apply every pending migration and return what was applied.

        Each file runs in its own transaction together with the row that records
        it, so a failure leaves neither the schema nor the ledger half updated.
        """
        applied = []

        for path in MigrationRunner.pending():
            statements = path.read_text(encoding="utf-8")

            with connection() as database, database.transaction():
                database.execute(statements)
                database.execute(
                    "INSERT INTO schema_migrations (name) VALUES (%s)",
                    (path.name,),
                )

            applied.append(path.name)

        return applied
