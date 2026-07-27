import threading
from typing import ClassVar

from app.config import settings
from app.core.instances import get_or_create
from app.rag.base import Retriever
from app.rag.registry import RetrieverRegistry


class RetrieverFactory:
    """Builds the retriever selected by `RETRIEVER_PROVIDER`, or the one asked
    for, against the collection asked for.

    The factory knows the registry and nothing else. Instances are shared per
    implementation and collection, so every agent may search its own collection
    while reusing one client.
    """

    _instances: ClassVar[dict[tuple[str, str], Retriever]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "", collection: str = "") -> Retriever:
        """Return a retriever.

        Args:
            name: Which retriever to build. Empty means the one configured by
                `RETRIEVER_PROVIDER`.
            collection: Which collection to search. Empty means the shared one
                from `QDRANT_COLLECTION`, which keeps every agent on one index
                unless it declares its own.

        Raises:
            ValueError: If the name is not registered.
        """
        implementation = RetrieverRegistry.get(name or settings.retriever_provider)
        key = (implementation.__name__, collection)

        return get_or_create(
            RetrieverFactory._instances,
            RetrieverFactory._lock,
            key,
            lambda: implementation(collection=collection),
        )
