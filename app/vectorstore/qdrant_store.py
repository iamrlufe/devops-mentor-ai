import uuid

from qdrant_client import QdrantClient, models

from app.config import settings
from app.embeddings.models import Embedding
from app.vectorstore.base import VectorStore
from app.vectorstore.models import SearchResult

COLLECTION_NAME = "mentor_documents"
DISTANCE = models.Distance.COSINE
POINT_ID_NAMESPACE = uuid.UUID("6f6f9d2c-2a5e-4a5f-9c2b-6c5a1d3e7b41")
UPSERT_BATCH_SIZE = 100

PAYLOAD_CHUNK_ID = "chunk_id"
PAYLOAD_METADATA = "metadata"


class QdrantVectorStore(VectorStore):

    def __init__(self, collection_name: str = COLLECTION_NAME):
        self.collection_name = collection_name
        self.client = QdrantClient(url=settings.qdrant_url)

    def create_collection(self, vector_size: int) -> None:
        if self.client.collection_exists(self.collection_name):
            self._check_vector_size(vector_size)
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=DISTANCE),
        )

    def upsert(self, embeddings: list[Embedding]) -> None:
        if not embeddings:
            return

        self.create_collection(len(embeddings[0].vector))

        points = [self._build_point(embedding) for embedding in embeddings]

        for start in range(0, len(points), UPSERT_BATCH_SIZE):
            self.client.upsert(
                collection_name=self.collection_name,
                points=points[start:start + UPSERT_BATCH_SIZE],
                wait=True,
            )

    def search(self, vector: list[float], limit: int = 5) -> list[SearchResult]:
        if not self.client.collection_exists(self.collection_name):
            raise RuntimeError(
                f"Collection '{self.collection_name}' does not exist. "
                "Index the documents before searching."
            )

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
        )

        return [self._build_result(point) for point in response.points]

    def delete_collection(self) -> None:
        if not self.client.collection_exists(self.collection_name):
            return

        self.client.delete_collection(collection_name=self.collection_name)

    @staticmethod
    def _build_point(embedding: Embedding) -> models.PointStruct:
        return models.PointStruct(
            id=str(uuid.uuid5(POINT_ID_NAMESPACE, embedding.chunk_id)),
            vector=embedding.vector,
            payload={
                PAYLOAD_CHUNK_ID: embedding.chunk_id,
                PAYLOAD_METADATA: dict(embedding.metadata),
            },
        )

    @staticmethod
    def _build_result(point: models.ScoredPoint) -> SearchResult:
        payload = point.payload or {}

        return SearchResult(
            chunk_id=payload.get(PAYLOAD_CHUNK_ID, ""),
            score=point.score,
            metadata=payload.get(PAYLOAD_METADATA) or {},
        )

    def _check_vector_size(self, vector_size: int) -> None:
        """Guard against writing vectors of another model into an existing collection."""
        config = self.client.get_collection(self.collection_name).config
        existing_size = config.params.vectors.size

        if existing_size != vector_size:
            raise RuntimeError(
                f"Collection '{self.collection_name}' stores vectors of size "
                f"{existing_size}, but got {vector_size}. Delete the collection or "
                "switch back to the previous embedding model."
            )
