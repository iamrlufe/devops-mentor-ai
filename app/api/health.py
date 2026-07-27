from collections.abc import Callable

from app.config import settings
from app.embeddings.factory import EmbeddingFactory
from app.memory.factory import MemoryFactory
from app.providers.factory import ProviderFactory
from app.rag.factory import RetrieverFactory
from app.vectorstore.factory import VectorStoreFactory

STATUS_OK = "ok"
STATUS_ERROR = "error"
STATUS_DEGRADED = "degraded"


def _probe(name: str, check: Callable[[], None]) -> dict[str, str]:
    """Run one component check and turn a failure into a reported status.

    A health endpoint must answer even when a component is down, so every
    exception becomes a status instead of a 500.
    """
    component = {"name": name, "status": STATUS_OK}

    try:
        check()
    except Exception as error:  # noqa: BLE001 - a health check reports, never raises
        component["status"] = STATUS_ERROR
        component["detail"] = f"{type(error).__name__}: {error}"

    return component


def _check_vector_store() -> None:
    """Ask Qdrant for its collections, which proves the connection works."""
    VectorStoreFactory.create().client.get_collections()


def collect_components() -> list[dict[str, str]]:
    """Return the state of every replaceable component."""
    return [
        _probe(f"llm:{settings.llm_provider}", ProviderFactory.create),
        _probe(f"embedding:{settings.embedding_provider}", EmbeddingFactory.create),
        _probe(f"memory:{settings.memory_provider}", MemoryFactory.create),
        _probe(f"retriever:{settings.retriever_provider}", RetrieverFactory.create),
        _probe(f"vector_store:{settings.qdrant_collection}", _check_vector_store),
    ]


def build_health(name: str, version: str) -> dict[str, object]:
    """Return the health document of the platform.

    The top level `status` stays `ok` while the service can answer, so existing
    monitoring keeps working; a broken component shows up as `degraded`.
    """
    components = collect_components()
    healthy = all(component["status"] == STATUS_OK for component in components)

    return {
        "status": STATUS_OK if healthy else STATUS_DEGRADED,
        "name": name,
        "version": version,
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
        "memory_provider": settings.memory_provider,
        "retriever_provider": settings.retriever_provider,
        "vector_store": {
            "url": settings.qdrant_url,
            "collection": settings.qdrant_collection,
        },
        "components": components,
    }
