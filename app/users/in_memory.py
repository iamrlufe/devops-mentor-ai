import threading

from app.users.base import UserStore
from app.users.models import UserProfile
from app.users.registry import UserRegistry


@UserRegistry.register("in_memory")
class InMemoryUserStore(UserStore):
    """Keeps the profiles in the process memory. They are lost on restart.

    The store is written from several handlers at once, so every access is
    guarded. The Telegram index is kept alongside the profiles so that looking a
    user up by their messenger id does not scan the whole store.
    """

    def __init__(self) -> None:
        self._profiles: dict[str, UserProfile] = {}
        self._by_telegram: dict[str, str] = {}
        self._lock = threading.Lock()

    def get(self, user_id: str) -> UserProfile | None:
        with self._lock:
            return self._profiles.get(user_id)

    def get_by_telegram_id(self, telegram_id: str) -> UserProfile | None:
        with self._lock:
            user_id = self._by_telegram.get(telegram_id)

            return self._profiles.get(user_id) if user_id else None

    def save(self, profile: UserProfile) -> None:
        with self._lock:
            self._profiles[profile.user_id] = profile

            if profile.telegram_id:
                self._by_telegram[profile.telegram_id] = profile.user_id

    def list(self) -> list[UserProfile]:
        with self._lock:
            return sorted(self._profiles.values(), key=lambda item: item.created_at)

    def delete(self, user_id: str) -> None:
        with self._lock:
            profile = self._profiles.pop(user_id, None)

            if profile is not None and profile.telegram_id:
                self._by_telegram.pop(profile.telegram_id, None)
