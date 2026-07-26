from app.core.registry import Registry
from app.embeddings.base import EmbeddingProvider


class EmbeddingRegistry(
    Registry[EmbeddingProvider],
    package="app.embeddings",
    label="embedding provider",
):
    """Maps the `EMBEDDING_PROVIDER` value to the embedding provider class."""
