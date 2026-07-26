from app.config import settings
from app.rag.base import Retriever
from app.rag.registry import RetrieverRegistry


class RetrieverFactory:
    """Builds the retriever selected by the `RETRIEVER_PROVIDER` setting.

    The factory knows the registry and nothing else. Instances are shared for
    the whole process.
    """

    _instances: dict[str, Retriever] = {}

    @staticmethod
    def create() -> Retriever:
        """Return the configured retriever.

        Raises:
            ValueError: If `RETRIEVER_PROVIDER` names something that is not registered.
        """
        name = settings.retriever_provider
        implementation = RetrieverRegistry.get(name)
        key = implementation.__name__

        if key not in RetrieverFactory._instances:
            RetrieverFactory._instances[key] = implementation()

        return RetrieverFactory._instances[key]
