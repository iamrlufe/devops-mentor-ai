from app.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.registry import EmbeddingRegistry


class EmbeddingFactory:
    """Builds the embedding provider selected by `EMBEDDING_PROVIDER`, or
    the one asked for.

    The factory knows the registry and nothing else. Instances are shared per
    implementation, so the clients behind them are built once.
    """

    _instances: dict[str, EmbeddingProvider] = {}

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

        if key not in EmbeddingFactory._instances:
            EmbeddingFactory._instances[key] = implementation()

        return EmbeddingFactory._instances[key]
