from app.embeddings.base import EmbeddingProvider
from app.embeddings.gemini_embedding import GeminiEmbeddingProvider


class EmbeddingFactory:
    _provider: EmbeddingProvider | None = None

    @staticmethod
    def create() -> EmbeddingProvider:
        """Return the embedding provider shared by the whole process."""
        if EmbeddingFactory._provider is None:
            EmbeddingFactory._provider = GeminiEmbeddingProvider()

        return EmbeddingFactory._provider
