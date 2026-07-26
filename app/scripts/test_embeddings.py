from app.chunking.models import Chunk
from app.embeddings.factory import EmbeddingFactory
from app.embeddings.service import EmbeddingService

PREVIEW_VALUES = 10

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
        text="A Kubernetes Deployment keeps the declared number of pod replicas running.",
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

provider = EmbeddingFactory.create()
print(f"Provider: {type(provider).__name__}")
print(f"Model: {provider.model}")
print(f"Chunks: {len(CHUNKS)}")

embeddings = EmbeddingService.embed_chunks(CHUNKS)

for embedding in embeddings:
    preview = ", ".join(f"{value:.6f}" for value in embedding.vector[:PREVIEW_VALUES])

    print(f"\nchunk id: {embedding.chunk_id}")
    print(f"  dimensions: {len(embedding.vector)}")
    print(f"  first {PREVIEW_VALUES}: [{preview}]")
    print(f"  metadata: {embedding.metadata}")
