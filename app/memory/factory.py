from app.memory.base import MemoryProvider
from app.memory.in_memory import InMemoryMemoryProvider


class MemoryFactory:
    _provider: MemoryProvider | None = None

    @staticmethod
    def create() -> MemoryProvider:
        """Return the memory provider shared by the whole process."""
        if MemoryFactory._provider is None:
            MemoryFactory._provider = InMemoryMemoryProvider()

        return MemoryFactory._provider
