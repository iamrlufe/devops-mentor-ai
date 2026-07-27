from dataclasses import dataclass, field, replace
from datetime import UTC, datetime


def now() -> datetime:
    """Return the current moment in UTC."""
    return datetime.now(UTC)

#: Fields a caller may change at runtime. Kept in one place so a new field is
#: added once instead of in the API, the bot and the manager.
MUTABLE_FIELDS = (
    "user_id",
    "agent",
    "provider",
    "embedding",
    "memory",
    "retriever",
    "collection",
    "prompt",
)


@dataclass(frozen=True)
class Workspace:
    """The stack one user works with.

    Every field is a name, never an object, and an empty name means "follow what
    the agent declares, and then the platform settings". The workspace is
    immutable: a change produces a new value, so a request can never observe a
    half-updated workspace.
    """

    chat_id: str
    #: Profile that owns this workspace. Empty for a workspace addressed
    #: directly over REST, which needs no profile.
    user_id: str = ""
    agent: str = ""
    provider: str = ""
    embedding: str = ""
    memory: str = ""
    retriever: str = ""
    collection: str = ""
    prompt: str = ""
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)

    def with_changes(self, **changes: str) -> "Workspace":
        """Return a copy with the given fields replaced.

        Args:
            **changes: Any of `MUTABLE_FIELDS`. `None` and missing values are
                ignored, so a partial update leaves the rest untouched.

        Raises:
            ValueError: If a field is not one a caller may change.
        """
        applied = {}

        for name, value in changes.items():
            if value is None:
                continue
            if name not in MUTABLE_FIELDS:
                raise ValueError(
                    f"Unknown workspace field: '{name}'. "
                    f"Known fields: {', '.join(MUTABLE_FIELDS)}."
                )
            applied[name] = value

        return replace(self, updated_at=now(), **applied)

    def as_dict(self) -> dict[str, str]:
        """Return the workspace as plain data for the API and the bot."""
        return {
            "chat_id": self.chat_id,
            **{name: getattr(self, name) for name in MUTABLE_FIELDS},
            "created_at": self.created_at.isoformat(timespec="seconds"),
            "updated_at": self.updated_at.isoformat(timespec="seconds"),
        }
