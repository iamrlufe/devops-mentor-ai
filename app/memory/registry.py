from app.core.registry import Registry
from app.memory.base import MemoryProvider


class MemoryRegistry(
    Registry[MemoryProvider],
    package="app.memory",
    label="memory provider",
):
    """Maps the `MEMORY_PROVIDER` value to the memory provider class."""
