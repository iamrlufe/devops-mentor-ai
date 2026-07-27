from typing import Any

from app.admin.base import AdminSource
from app.admin.registry import AdminRegistry
from app.admin.repositories import AdminRepository
from app.database.repositories.metrics_repository import MetricsRepository


@AdminRegistry.register("postgres")
class PostgresAdminSource(AdminSource):
    """Reads the administration numbers from PostgreSQL.

    The class only forwards to repositories: the SQL lives there, the meaning
    lives in the service above.
    """

    def counters(self) -> dict[str, Any]:
        return AdminRepository.counters()

    def users(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        return AdminRepository.users(limit, offset)

    def user_statistics(self, user_id: str) -> dict[str, Any]:
        return AdminRepository.user_statistics(user_id)

    def user_memory(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return AdminRepository.user_memory(user_id, limit)

    def user_history(self, user_id: str, limit: int = 100) -> list[dict[str, Any]]:
        return AdminRepository.user_history(user_id, limit)

    def conversations(
        self,
        user_id: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        return AdminRepository.conversations(user_id, limit, offset)

    def messages(self, conversation_id: str, limit: int = 200) -> list[dict[str, Any]]:
        return AdminRepository.messages(conversation_id, limit)

    def registrations(self, days: int = 7) -> list[dict[str, Any]]:
        return AdminRepository.registrations(days)

    def messages_per_day(self, days: int = 7) -> list[dict[str, Any]]:
        return AdminRepository.messages_per_day(days)

    def usage(self, column: str) -> list[dict[str, Any]]:
        return MetricsRepository.usage_of(column)

    def workspace_selections(self, column: str) -> list[dict[str, Any]]:
        return AdminRepository.workspace_selections(column)

    def agent_usage(self) -> list[dict[str, Any]]:
        return AdminRepository.agent_usage()

    def provider_usage(self) -> list[dict[str, Any]]:
        return MetricsRepository.by_provider()

    def request_totals(self) -> dict[str, Any]:
        return MetricsRepository.totals()
