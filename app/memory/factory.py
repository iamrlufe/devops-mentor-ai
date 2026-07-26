from app.config import settings
from app.memory.base import MemoryProvider
from app.memory.registry import MemoryRegistry


class MemoryFactory:
    """Builds the memory provider selected by the `MEMORY_PROVIDER` setting.

    The factory knows the registry and nothing else. Instances are shared for
    the whole process, which is what keeps the conversation history alive.
    """

    _instances: dict[str, MemoryProvider] = {}

    @staticmethod
    def create() -> MemoryProvider:
        """Return the configured memory provider.

        Raises:
            ValueError: If `MEMORY_PROVIDER` names something that is not registered.
        """
        name = settings.memory_provider
        implementation = MemoryRegistry.get(name)
        key = implementation.__name__

        if key not in MemoryFactory._instances:
            MemoryFactory._instances[key] = implementation()

        return MemoryFactory._instances[key]
