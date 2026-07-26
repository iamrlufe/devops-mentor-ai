import sys

from app.rag.context_builder import ContextBuilder
from app.rag.factory import RetrieverFactory

SAMPLE_DOCUMENTS = [
    "Docker builds an image from a Dockerfile with `docker build -t app .`",
    "A Kubernetes Deployment keeps the declared number of pod replicas running.",
]

query = sys.argv[1] if len(sys.argv) > 1 else "How do I build a Docker image?"

retriever = RetrieverFactory.create()
print(f"Retriever: {type(retriever).__name__}")
print(f"Query: {query}")

documents = retriever.search(query)
print(f"Found documents: {len(documents)}")

for number, document in enumerate(documents, start=1):
    print(f"{number}. {document}")

print("\nContext:")
print(repr(ContextBuilder.build(documents)))

print("\nContext for sample documents:")
print(ContextBuilder.build(SAMPLE_DOCUMENTS))
