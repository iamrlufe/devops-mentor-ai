from typing import Any

from app.admin.factory import AdminFactory
from app.admin.models import Statistics
from app.organizations.manager import OrganizationManager

DEFAULT_WINDOW_DAYS = 7

#: Which recorded selection answers which statistic. Data, not branching: a new
#: replaceable layer is one more entry.
USAGE_COLUMNS = {
    "agents_usage": "agent",
    "providers_usage": "provider",
    "embeddings_usage": "embedding",
    "memory_usage": "memory",
    "retrievers_usage": "retriever",
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


class StatisticsService:
    """Builds the breakdowns the administration reports."""

    @staticmethod
    def build(days: int = DEFAULT_WINDOW_DAYS) -> Statistics:
        """Return the platform statistics over a window of days."""
        source = AdminFactory.create()
        counters = source.counters()
        totals = source.request_totals()

        usage = {
            name: _serialise(source.usage(column))
            for name, column in USAGE_COLUMNS.items()
        }

        return Statistics(
            users={
                "total": counters["users_total"],
                "active_today": counters["active_today"],
                "active_week": counters["active_week"],
                "registered_today": counters["registrations_today"],
            },
            registrations=_serialise(source.registrations(days)),
            messages=_serialise(source.messages_per_day(days)),
            organizations=[
                organization.as_dict()
                for organization in OrganizationManager.list()
            ],
            workspaces={
                "total": counters["workspaces_total"],
                "by_agent": _serialise(source.workspace_selections("agent")),
                "by_provider": _serialise(source.workspace_selections("provider")),
            },
            average_response_time_ms=int(totals["average_latency_ms"] or 0),
            **usage,
        )
