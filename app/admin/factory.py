import threading
from typing import ClassVar

from app.admin.base import AdminSource
from app.admin.registry import AdminRegistry
from app.config import settings
from app.core.instances import get_or_create


class AdminFactory:
    """Builds the administration source selected by `ADMIN_SOURCE`."""

    _instances: ClassVar[dict[str, AdminSource]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "") -> AdminSource:
        """Return the administration source.

        Raises:
            ValueError: If the name is not registered.
        """
        implementation = AdminRegistry.get(name or settings.admin_source)
        key = implementation.__name__

        return get_or_create(
            AdminFactory._instances,
            AdminFactory._lock,
            key,
            lambda: implementation(),
        )
