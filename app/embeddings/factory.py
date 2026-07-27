import threading
from typing import ClassVar

from app.config import settings
from app.core.instances import get_or_create
from app.embeddings.base import EmbeddingProvider
from app.embeddings.registry import EmbeddingRegistry


class EmbeddingFactory:
    """Builds the embedding provider selected by `EMBEDDING_PROVIDER`, or
    the one asked for.

    The factory knows the registry and nothing else. Instances are shared per
    implementation, so the clients behind them are built once.
    """

    _instances: ClassVar[dict[str, EmbeddingProvider]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "") -> EmbeddingProvider:
        """Return a embedding provider.

        Args:
            name: Which implementation to build. Empty means the one configured
                by `EMBEDDING_PROVIDER`, which lets an agent declare its own without any
                change to the calling code.

        Raises:
            ValueError: If the name is not registered.
        """
        implementation = EmbeddingRegistry.get(name or settings.embedding_provider)
        key = implementation.__name__

        return get_or_create(
            EmbeddingFactory._instances,
            EmbeddingFactory._lock,
            key,
            lambda: implementation(),
        )
