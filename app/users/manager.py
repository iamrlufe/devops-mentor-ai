from app.config import settings
from app.users.factory import UserFactory
from app.users.models import UserProfile, new_user_id


class UserManager:
    """Reads and updates user profiles.

    A profile is created on first contact, without registration or login: the
    messenger identifier is only an external key, and everything else in the
    platform works with the `user_id` this manager hands out.
    """

    @staticmethod
    def get(user_id: str) -> UserProfile | None:
        """Return a profile by platform user id, or `None`."""
        return UserFactory.create().get(user_id)

    @staticmethod
    def get_by_telegram_id(telegram_id: str) -> UserProfile | None:
        """Return the profile linked to a Telegram account, or `None`."""
        return UserFactory.create().get_by_telegram_id(str(telegram_id))

    @staticmethod
    def ensure_telegram_user(telegram_id: str) -> tuple[UserProfile, bool]:
        """Return the profile of a Telegram user, creating it on first contact.

        Returns:
            The profile and whether it was created by this call, so the caller
            can start the first-run questions.
        """
        store = UserFactory.create()
        existing = store.get_by_telegram_id(str(telegram_id))

        if existing is not None:
            return existing, False

        profile = UserProfile(
            user_id=new_user_id(),
            telegram_id=str(telegram_id),
            language=settings.default_language,
            timezone=settings.default_timezone,
        )
        store.save(profile)

        return profile, True

    @staticmethod
    def update(user_id: str, **changes: object) -> UserProfile:
        """Change part of a profile and store it.

        Raises:
            ValueError: If the profile does not exist or a field is unknown.
        """
        store = UserFactory.create()
        profile = store.get(user_id)

        if profile is None:
            raise ValueError(f"Unknown user: '{user_id}'.")

        updated = profile.with_changes(**changes)
        store.save(updated)

        return updated

    @staticmethod
    def list() -> list[UserProfile]:
        """Return every known profile."""
        return UserFactory.create().list()
