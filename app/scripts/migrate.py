from app.config import settings
from app.database.connection import reset_pools
from app.database.migrations import MigrationRunner

print(
    f"Database: {settings.postgres_host}:{settings.postgres_port}"
    f"/{settings.postgres_db}"
)

pending = [path.name for path in MigrationRunner.pending()]

if not pending:
    print("Nothing to apply, the schema is up to date.")
else:
    print("Pending: " + ", ".join(pending))

    for name in MigrationRunner.run():
        print(f"Applied {name}")

print("Applied migrations: " + ", ".join(sorted(MigrationRunner.applied())))
reset_pools()
