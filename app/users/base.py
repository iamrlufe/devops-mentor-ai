from abc import ABC, abstractmethod

from app.users.models import UserProfile


class UserStore(ABC):
    """Where user profiles live.

    The in-process store ships with the platform; a persistent one is a new
    class registered under a new name, with nothing else to change.
    """

    @abstractmethod
    def get(self, user_id: str) -> UserProfile | None:
        """Return the profile with this platform user id, or `None`."""
        raise NotImplementedError

    @abstractmethod
    def get_by_telegram_id(self, telegram_id: str) -> UserProfile | None:
        """Return the profile linked to a Telegram account, or `None`."""
        raise NotImplementedError

    @abstractmethod
    def save(self, profile: UserProfile) -> None:
        """Store a profile, replacing the one with the same user id."""
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[UserProfile]:
        """Return every stored profile."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: str) -> None:
        """Forget a profile. Missing ids are ignored."""
        raise NotImplementedError
