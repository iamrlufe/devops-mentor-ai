from typing import Any

from app.database.repositories.user_repository import UserRepository
from app.users.base import UserStore
from app.users.models import UserProfile
from app.users.registry import UserRegistry


def to_profile(row: dict[str, Any]) -> UserProfile:
    """Turn a database row into a profile."""
    return UserProfile(
        user_id=row["user_id"],
        telegram_id=row["telegram_id"] or "",
        name=row["name"],
        phone=row["phone"],
        language=row["language"],
        timezone=row["timezone"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        preferred_agent=row["preferred_agent"],
        preferred_provider=row["preferred_provider"],
        last_seen=row["last_seen"],
        last_agent=row["last_agent"],
        last_provider=row["last_provider"],
        message_count=row["message_count"],
        conversation_count=row["conversation_count"],
        registration_source=row["registration_source"],
        metadata=dict(row["metadata"] or {}),
    )


def to_row(profile: UserProfile) -> dict[str, Any]:
    """Turn a profile into the values the repository expects."""
    return {
        "user_id": profile.user_id,
        "telegram_id": profile.telegram_id or None,
        "name": profile.name,
        "phone": profile.phone,
        "language": profile.language,
        "timezone": profile.timezone,
        "preferred_agent": profile.preferred_agent,
        "preferred_provider": profile.preferred_provider,
        "last_agent": profile.last_agent,
        "last_provider": profile.last_provider,
        "message_count": profile.message_count,
        "conversation_count": profile.conversation_count,
        "registration_source": profile.registration_source,
        "metadata": profile.metadata,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
        "last_seen": profile.last_seen,
    }


@UserRegistry.register("postgres")
class PostgresUserStore(UserStore):
    """Keeps the profiles in PostgreSQL, so they survive a restart.

    The store maps between profiles and rows; the SQL lives in the repository.
    """

    def get(self, user_id: str) -> UserProfile | None:
        row = UserRepository.get(user_id)

        return to_profile(row) if row else None

    def get_by_telegram_id(self, telegram_id: str) -> UserProfile | None:
        row = UserRepository.get_by_telegram_id(telegram_id)

        return to_profile(row) if row else None

    def save(self, profile: UserProfile) -> None:
        UserRepository.upsert(to_row(profile))

    def list(self) -> list[UserProfile]:
        return [to_profile(row) for row in UserRepository.list()]

    def delete(self, user_id: str) -> None:
        UserRepository.delete(user_id)
