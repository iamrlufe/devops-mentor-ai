import threading
from typing import ClassVar

from app.config import settings
from app.core.instances import get_or_create
from app.organizations.base import OrganizationStore
from app.organizations.registry import OrganizationRegistry


class OrganizationFactory:
    """Builds the organization store selected by `ORGANIZATION_STORE`."""

    _instances: ClassVar[dict[str, OrganizationStore]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "") -> OrganizationStore:
        """Return the organization store.

        Raises:
            ValueError: If the name is not registered.
        """
        implementation = OrganizationRegistry.get(name or settings.organization_store)
        key = implementation.__name__

        return get_or_create(
            OrganizationFactory._instances,
            OrganizationFactory._lock,
            key,
            lambda: implementation(),
        )
