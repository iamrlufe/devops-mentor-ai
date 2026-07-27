from typing import Any

from app.database.connection import connection

INSERT = """
INSERT INTO request_metrics (
    organization_id, user_id, chat_id, agent, provider, embedding, retriever,
    memory, latency_ms, success, error
)
VALUES (
    %(organization_id)s, %(user_id)s, %(chat_id)s, %(agent)s, %(provider)s,
    %(embedding)s, %(retriever)s, %(memory)s, %(latency_ms)s, %(success)s,
    %(error)s
)
"""


class MetricsRepository:
    """Every SQL statement about request metrics.

    One row per answered or failed request. This is where latency, error counts
    and provider usage are read from, so the administration never has to guess
    them from the conversation tables.
    """

    @staticmethod
    def record(values: dict[str, Any]) -> None:
        """Store one request."""
        with connection() as database:
            database.execute(INSERT, values)

    @staticmethod
    def by_provider() -> list[dict[str, Any]]:
        """Return usage, errors and latency per provider."""
        with connection() as database:
            return database.execute(
                "SELECT provider, count(*) AS requests, "
                "count(*) FILTER (WHERE NOT success) AS errors, "
                "coalesce(round(avg(latency_ms) FILTER (WHERE success)), 0) "
                "AS average_latency_ms, "
                "count(DISTINCT user_id) FILTER (WHERE user_id <> '') AS users "
                "FROM request_metrics GROUP BY provider ORDER BY requests DESC"
            ).fetchall()

    @staticmethod
    def by_agent() -> list[dict[str, Any]]:
        """Return usage per agent."""
        with connection() as database:
            return database.execute(
                "SELECT agent, count(*) AS requests, "
                "count(DISTINCT user_id) FILTER (WHERE user_id <> '') AS users "
                "FROM request_metrics GROUP BY agent ORDER BY requests DESC"
            ).fetchall()

    @staticmethod
    def usage_of(column: str) -> list[dict[str, Any]]:
        """Return usage per value of one recorded column.

        Args:
            column: Which recorded selection to group by. Only the columns of
                this table are accepted, so the name can never carry SQL.

        Raises:
            ValueError: If the column is not one of the recorded selections.
        """
        allowed = {"agent", "provider", "embedding", "retriever", "memory"}

        if column not in allowed:
            raise ValueError(
                f"Unknown metric column: '{column}'. "
                f"Known: {', '.join(sorted(allowed))}."
            )

        with connection() as database:
            return database.execute(
                f"SELECT {column} AS name, count(*) AS requests "  # noqa: S608
                "FROM request_metrics WHERE "
                f"{column} <> '' GROUP BY {column} ORDER BY requests DESC"
            ).fetchall()

    @staticmethod
    def totals() -> dict[str, Any]:
        """Return overall request counters and the average response time."""
        with connection() as database:
            return database.execute(
                "SELECT count(*) AS requests, "
                "count(*) FILTER (WHERE NOT success) AS errors, "
                "count(*) FILTER (WHERE created_at >= current_date) AS today, "
                "coalesce(round(avg(latency_ms) FILTER (WHERE success)), 0) "
                "AS average_latency_ms FROM request_metrics"
            ).fetchone()
