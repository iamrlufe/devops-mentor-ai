from app.chunking.models import Chunk
from app.embeddings.service import EmbeddingService
from app.rag.context_builder import ContextBuilder
from app.rag.factory import RetrieverFactory
from app.rag.qdrant_retriever import TEXT_KEY
from app.vectorstore.factory import VectorStoreFactory
from app.vectorstore.service import VectorStoreService

QUERY = "How do I build a Docker image?"
LIMIT = 2

CHUNKS = [
    Chunk(
        id="test-docker-0001",
        document_id="test-docker",
        text="Docker builds an image from a Dockerfile with `docker build -t app .`",
        order=1,
        metadata={"title": "Docker Basics", "source": "docs/docker.md"},
    ),
    Chunk(
        id="test-kubernetes-0001",
        document_id="test-kubernetes",
        text="A Kubernetes Deployment keeps the declared number of pod replicas running.",
        order=1,
        metadata={"title": "Deployments", "source": "docs/kubernetes.md"},
    ),
    Chunk(
        id="test-ci-0001",
        document_id="test-ci",
        text="A CI pipeline runs tests on every push and blocks a broken merge.",
        order=1,
        metadata={"title": "CI Pipelines", "source": "docs/ci.md"},
    ),
]

# The payload of a point carries only chunk_id and metadata, so the text of the
# chunk travels to Qdrant inside the metadata. Any indexing job must do the same.
for chunk in CHUNKS:
    chunk.metadata[TEXT_KEY] = chunk.text

store = VectorStoreFactory.create()
collection_existed = store.client.collection_exists(store.collection_name)

try:
    embeddings = EmbeddingService.embed_chunks(CHUNKS)
    print(f"Embeddings: {len(embeddings)} x {len(embeddings[0].vector)}")

    indexed = VectorStoreService.index_embeddings(embeddings)
    print(f"Indexed: {indexed}")

    retriever = RetrieverFactory.create()
    print(f"Retriever: {type(retriever).__name__}")

    documents = retriever.search(QUERY, limit=LIMIT)

    print(f"\nQuery: {QUERY}")
    print(f"Found documents: {len(documents)}")

    for document in documents:
        print(f"\n  id: {document.id}")
        print(f"  score: {document.score:.4f}")
        print(f"  title: {document.metadata.get('title')}")
        print(f"  source: {document.metadata.get('source')}")

    print("\nContext:\n")
    print(ContextBuilder.build(documents))
finally:
    if collection_existed:
        print(
            f"\nCollection '{store.collection_name}' already existed, "
            "test points were left in place."
        )
    else:
        store.delete_collection()
        print(f"\nCollection deleted: {store.collection_name}")
