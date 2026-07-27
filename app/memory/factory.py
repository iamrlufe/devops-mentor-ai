import threading
from typing import ClassVar

from app.config import settings
from app.core.instances import get_or_create
from app.memory.base import MemoryProvider
from app.memory.registry import MemoryRegistry


class MemoryFactory:
    """Builds the memory provider selected by `MEMORY_PROVIDER`, or the one asked for.

    The factory knows the registry and nothing else. Instances are shared per
    implementation, so the clients behind them are built once.
    """

    _instances: ClassVar[dict[str, MemoryProvider]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "") -> MemoryProvider:
        """Return a memory provider.

        Args:
            name: Which implementation to build. Empty means the one configured
                by `MEMORY_PROVIDER`, which lets an agent declare its own without any
                change to the calling code.

        Raises:
            ValueError: If the name is not registered.
        """
        implementation = MemoryRegistry.get(name or settings.memory_provider)
        key = implementation.__name__

        return get_or_create(
            MemoryFactory._instances,
            MemoryFactory._lock,
            key,
            lambda: implementation(),
        )
