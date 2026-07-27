from app.config import settings
from app.memory.base import MemoryProvider
from app.memory.registry import MemoryRegistry


class MemoryFactory:
    """Builds the memory provider selected by `MEMORY_PROVIDER`, or the one asked for.

    The factory knows the registry and nothing else. Instances are shared per
    implementation, so the clients behind them are built once.
    """

    _instances: dict[str, MemoryProvider] = {}

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

        if key not in MemoryFactory._instances:
            MemoryFactory._instances[key] = implementation()

        return MemoryFactory._instances[key]
