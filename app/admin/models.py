from dataclasses import dataclass, field

ROLE_ADMIN = "admin"
ROLE_USER = "user"


@dataclass(frozen=True)
class AdminIdentity:
    """Who is asking, and what they are allowed to do."""

    role: str = ROLE_USER
    subject: str = ""
    source: str = ""

    @property
    def is_admin(self) -> bool:
        """Whether this identity may read the administration."""
        return self.role == ROLE_ADMIN

    def as_dict(self) -> dict[str, str]:
        """Return the identity as plain data."""
        return {"role": self.role, "subject": self.subject, "source": self.source}


@dataclass(frozen=True)
class Dashboard:
    """The counters an operator sees first."""

    version: str = ""
    uptime_seconds: int = 0
    users_total: int = 0
    active_today: int = 0
    active_week: int = 0
    messages_total: int = 0
    messages_today: int = 0
    conversations_total: int = 0
    documents_total: int = 0
    collections_total: int = 0
    agents_total: int = 0
    providers_total: int = 0
    embedding_providers_total: int = 0
    memory_providers_total: int = 0
    retrievers_total: int = 0
    organizations_total: int = 0
    workspaces_total: int = 0

    def as_dict(self) -> dict[str, object]:
        """Return the dashboard as plain data."""
        return {
            "version": self.version,
            "uptime": self.uptime_seconds,
            "users_total": self.users_total,
            "active_today": self.active_today,
            "active_week": self.active_week,
            "messages_total": self.messages_total,
            "messages_today": self.messages_today,
            "conversations_total": self.conversations_total,
            "documents_total": self.documents_total,
            "collections_total": self.collections_total,
            "agents_total": self.agents_total,
            "providers_total": self.providers_total,
            "embedding_providers_total": self.embedding_providers_total,
            "memory_providers_total": self.memory_providers_total,
            "retrievers_total": self.retrievers_total,
            "organizations_total": self.organizations_total,
            "workspaces_total": self.workspaces_total,
        }


@dataclass(frozen=True)
class Statistics:
    """The breakdowns an operator asks for after the dashboard."""

    users: dict[str, int] = field(default_factory=dict)
    registrations: list[dict[str, object]] = field(default_factory=list)
    messages: list[dict[str, object]] = field(default_factory=list)
    agents_usage: list[dict[str, object]] = field(default_factory=list)
    providers_usage: list[dict[str, object]] = field(default_factory=list)
    embeddings_usage: list[dict[str, object]] = field(default_factory=list)
    memory_usage: list[dict[str, object]] = field(default_factory=list)
    retrievers_usage: list[dict[str, object]] = field(default_factory=list)
    organizations: list[dict[str, object]] = field(default_factory=list)
    workspaces: dict[str, object] = field(default_factory=dict)
    average_response_time_ms: int = 0

    def as_dict(self) -> dict[str, object]:
        """Return the statistics as plain data."""
        return {
            "users": self.users,
            "registrations": self.registrations,
            "messages": self.messages,
            "agents_usage": self.agents_usage,
            "providers_usage": self.providers_usage,
            "embeddings_usage": self.embeddings_usage,
            "memory_usage": self.memory_usage,
            "retrievers_usage": self.retrievers_usage,
            "organizations": self.organizations,
            "workspaces": self.workspaces,
            "average_response_time": self.average_response_time_ms,
        }
