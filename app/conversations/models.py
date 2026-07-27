import uuid
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime

CONVERSATION_ID_PREFIX = "cnv_"
CONVERSATION_ID_LENGTH = 12


def new_conversation_id() -> str:
    """Return a fresh conversation id, for example `cnv_5c1a90b7e3d2`."""
    return f"{CONVERSATION_ID_PREFIX}{uuid.uuid4().hex[:CONVERSATION_ID_LENGTH]}"


def now() -> datetime:
    """Return the current moment in UTC."""
    return datetime.now(UTC)


@dataclass(frozen=True)
class ConversationMessage:
    """One stored turn of a conversation."""

    conversation_id: str
    role: str
    message: str
    user_id: str = ""
    agent: str = ""
    provider: str = ""
    tokens: int = 0
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=now)
    message_id: int = 0

    def as_dict(self) -> dict[str, object]:
        """Return the message as plain data."""
        return {
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "agent": self.agent,
            "provider": self.provider,
            "role": self.role,
            "message": self.message,
            "tokens": self.tokens,
            "created_at": self.created_at.isoformat(timespec="seconds"),
        }


@dataclass(frozen=True)
class Conversation:
    """A thread between one user and one agent.

    A conversation is the source of truth of what was said. Memory keeps only
    the recent window that goes into the prompt, so it can be trimmed or lost
    without losing the history.
    """

    conversation_id: str
    user_id: str = ""
    chat_id: str = ""
    agent: str = ""
    provider: str = ""
    title: str = ""
    message_count: int = 0
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)

    def with_changes(self, **changes: object) -> "Conversation":
        """Return a copy with the given fields replaced and `updated_at` bumped."""
        applied = {name: value for name, value in changes.items() if value is not None}

        return replace(self, updated_at=now(), **applied)

    def as_dict(self) -> dict[str, object]:
        """Return the conversation as plain data."""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "agent": self.agent,
            "provider": self.provider,
            "title": self.title,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(timespec="seconds"),
            "updated_at": self.updated_at.isoformat(timespec="seconds"),
        }
