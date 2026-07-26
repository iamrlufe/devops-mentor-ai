from app.chunking.models import Chunk
from app.embeddings.factory import EmbeddingFactory
from app.embeddings.models import Embedding


class EmbeddingService:

    @staticmethod
    def embed_chunks(chunks: list[Chunk]) -> list[Embedding]:
        """Embed the chunks, keeping their order and their metadata."""
        if not chunks:
            return []

        provider = EmbeddingFactory.create()
        vectors = provider.embed([chunk.text for chunk in chunks])

        if len(vectors) != len(chunks):
            raise RuntimeError(
                f"Got {len(vectors)} vectors for {len(chunks)} chunks."
            )

        return [
            Embedding(
                chunk_id=chunk.id,
                vector=vector,
                metadata=dict(chunk.metadata),
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
