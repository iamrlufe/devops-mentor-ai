from app.chunking.models import Chunk
from app.embeddings.factory import EmbeddingFactory
from app.embeddings.service import EmbeddingService
from app.vectorstore.qdrant_store import QdrantVectorStore

TEST_COLLECTION = "mentor_documents_test"
QUERY = "How do I build a Docker image?"
LIMIT = 3

CHUNKS = [
    Chunk(
        id="docker-0001",
        document_id="docker",
        text="Docker builds an image from a Dockerfile with `docker build -t app .`",
        order=1,
        metadata={"title": "Docker Basics", "source": "docs/docker.md"},
    ),
    Chunk(
        id="kubernetes-0001",
        document_id="kubernetes",
        text=(
            "A Kubernetes Deployment keeps the declared number of pod "
            "replicas running."
        ),
        order=1,
        metadata={"title": "Deployments", "source": "docs/kubernetes.md"},
    ),
    Chunk(
        id="ci-0001",
        document_id="ci",
        text="A CI pipeline runs tests on every push and blocks a broken merge.",
        order=1,
        metadata={"title": "CI Pipelines", "source": "docs/ci.md"},
    ),
]

embeddings = EmbeddingService.embed_chunks(CHUNKS)
print(f"Embeddings: {len(embeddings)} x {len(embeddings[0].vector)}")

store = QdrantVectorStore(collection_name=TEST_COLLECTION)

try:
    store.create_collection(len(embeddings[0].vector))
    print(f"Collection created: {TEST_COLLECTION}")

    store.upsert(embeddings)
    print(f"Stored embeddings: {len(embeddings)}")

    query_vector = EmbeddingFactory.create().embed_query(QUERY)
    results = store.search(query_vector, limit=LIMIT)

    print(f"\nQuery: {QUERY}")
    print(f"Results: {len(results)}")

    for result in results:
        print(f"\n  score: {result.score:.4f}")
        print(f"  chunk_id: {result.chunk_id}")
        print(f"  metadata: {result.metadata}")
finally:
    store.delete_collection()
    print(f"\nCollection deleted: {TEST_COLLECTION}")
