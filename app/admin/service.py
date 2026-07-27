import time
from typing import Any

from app.admin.factory import AdminFactory
from app.admin.manager import AdminManager
from app.admin.models import Dashboard
from app.admin.statistics import StatisticsService
from app.organizations.manager import OrganizationManager

#: When this process started, used for the uptime the dashboard reports.
STARTED_AT = time.monotonic()


class AdminService:
    """The only administration entry point a client ever calls.

    Telegram, a web dashboard and a CLI all go through this service, so none of
    them holds a rule, a query or a count of its own.
    """

    @staticmethod
    def dashboard(version: str) -> dict[str, Any]:
        """Return the counters an operator sees first."""
        counters = AdminFactory.create().counters()
        vector = AdminManager.vector_store_counts()

        return Dashboard(
            version=version,
            uptime_seconds=int(time.monotonic() - STARTED_AT),
            users_total=counters["users_total"],
            active_today=counters["active_today"],
            active_week=counters["active_week"],
            messages_total=counters["messages_total"],
            messages_today=counters["messages_today"],
            conversations_total=counters["conversations_total"],
            organizations_total=counters["organizations_total"],
            workspaces_total=counters["workspaces_total"],
            **vector,
            **AdminManager.registry_sizes(),
        ).as_dict()

    @staticmethod
    def statistics(days: int = 7) -> dict[str, Any]:
        """Return the breakdowns behind the dashboard."""
        return StatisticsService.build(days).as_dict()

    @staticmethod
    def users(limit: int = 100, offset: int = 0) -> dict[str, Any]:
        """Return the profiles of the platform."""
        users = _serialise(AdminManager.users(limit, offset))

        return {"count": len(users), "users": users}

    @staticmethod
    def user(user_id: str) -> dict[str, Any] | None:
        """Return one profile, or `None` when it does not exist."""
        return AdminManager.user(user_id)

    @staticmethod
    def user_workspace(user_id: str) -> dict[str, Any]:
        """Return the workspace of a user with what it resolves to."""
        return AdminManager.workspace(user_id)

    @staticmethod
    def user_history(user_id: str, limit: int = 100) -> dict[str, Any]:
        """Return the newest messages of a user."""
        history = _serialise(AdminFactory.create().user_history(user_id, limit))

        return {"user_id": user_id, "count": len(history), "messages": history}

    @staticmethod
    def user_memory(user_id: str, limit: int = 50) -> dict[str, Any]:
        """Return the memory windows of a user."""
        memory = _serialise(AdminFactory.create().user_memory(user_id, limit))

        return {"user_id": user_id, "count": len(memory), "memory": memory}

    @staticmethod
    def user_statistics(user_id: str) -> dict[str, Any]:
        """Return what one user has produced."""
        statistics = dict(AdminFactory.create().user_statistics(user_id))
        statistics["user_id"] = user_id

        return statistics

    @staticmethod
    def conversations(
        user_id: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Return conversations, newest first."""
        rows = _serialise(AdminFactory.create().conversations(user_id, limit, offset))

        return {"count": len(rows), "conversations": rows}

    @staticmethod
    def conversation(conversation_id: str) -> dict[str, Any] | None:
        """Return one conversation, or `None` when it does not exist."""
        rows = AdminFactory.create().conversations(limit=1000)

        for row in rows:
            if row["conversation_id"] == conversation_id:
                return _serialise([row])[0]

        return None

    @staticmethod
    def messages(conversation_id: str, limit: int = 200) -> dict[str, Any]:
        """Return the messages of a conversation."""
        rows = _serialise(AdminFactory.create().messages(conversation_id, limit))

        return {
            "conversation_id": conversation_id,
            "count": len(rows),
            "messages": rows,
        }

    @staticmethod
    def agents() -> dict[str, Any]:
        """Return every agent with how much it is used."""
        agents = AdminManager.agents()

        return {"count": len(agents), "agents": agents}

    @staticmethod
    def providers() -> dict[str, Any]:
        """Return every provider with how it has behaved."""
        providers = AdminManager.providers()

        return {"count": len(providers), "providers": providers}

    @staticmethod
    def organizations() -> dict[str, Any]:
        """Return every organization."""
        organizations = [
            organization.as_dict() for organization in OrganizationManager.list()
        ]

        return {"count": len(organizations), "organizations": organizations}

    @staticmethod
    def workspaces(limit: int = 100) -> dict[str, Any]:
        """Return the stored workspaces."""
        from app.workspaces.manager import WorkspaceManager

        stored = WorkspaceManager.list()[:limit]

        return {
            "count": len(stored),
            "workspaces": [workspace.as_dict() for workspace in stored],
        }


def _serialise(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Turn database rows into JSON friendly dictionaries."""
    return [
        {
            key: value.isoformat() if hasattr(value, "isoformat") else value
            for key, value in row.items()
        }
        for row in rows
    ]
