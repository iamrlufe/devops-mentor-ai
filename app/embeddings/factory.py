from app.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.registry import EmbeddingRegistry


class EmbeddingFactory:
    """Builds the embedding provider selected by the `EMBEDDING_PROVIDER` setting.

    The factory knows the registry and nothing else. Instances are shared for
    the whole process, so the API client is built once.
    """

    _instances: dict[str, EmbeddingProvider] = {}

    @staticmethod
    def create() -> EmbeddingProvider:
        """Return the configured embedding provider.

        Raises:
            ValueError: If `EMBEDDING_PROVIDER` names something that is not registered.
        """
        name = settings.embedding_provider
        implementation = EmbeddingRegistry.get(name)
        key = implementation.__name__

        if key not in EmbeddingFactory._instances:
            EmbeddingFactory._instances[key] = implementation()

        return EmbeddingFactory._instances[key]
