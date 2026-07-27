import threading
from typing import ClassVar

from app.config import settings
from app.core.instances import get_or_create
from app.users.base import UserStore
from app.users.registry import UserRegistry


class UserFactory:
    """Builds the user store selected by `USER_STORE`.

    The factory knows the registry and nothing else. One instance is shared for
    the whole process, which is what makes a profile visible to every handler.
    """

    _instances: ClassVar[dict[str, UserStore]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "") -> UserStore:
        """Return the user store.

        Args:
            name: Which store to build. Empty means the configured one.

        Raises:
            ValueError: If the name is not registered.
        """
        implementation = UserRegistry.get(name or settings.user_store)
        key = implementation.__name__

        return get_or_create(
            UserFactory._instances,
            UserFactory._lock,
            key,
            lambda: implementation(),
        )
