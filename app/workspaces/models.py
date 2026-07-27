from dataclasses import dataclass, replace

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

    def with_changes(self, **changes: str) -> "Workspace":
        """Return a copy with the given fields replaced.

        Args:
            **changes: Any of `MUTABLE_FIELDS`. `None` and missing values are
                ignored, so a partial update leaves the rest untouched.

        Raises:
            ValueError: If a field is not one a caller may change.
        """
        applied = {}

        for field, value in changes.items():
            if value is None:
                continue
            if field not in MUTABLE_FIELDS:
                raise ValueError(
                    f"Unknown workspace field: '{field}'. "
                    f"Known fields: {', '.join(MUTABLE_FIELDS)}."
                )
            applied[field] = value

        return replace(self, **applied)

    def as_dict(self) -> dict[str, str]:
        """Return the workspace as plain data for the API and the bot."""
        return {
            "chat_id": self.chat_id,
            **{field: getattr(self, field) for field in MUTABLE_FIELDS},
        }
