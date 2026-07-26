from app.core.registry import Registry
from app.rag.base import Retriever


class RetrieverRegistry(Registry[Retriever], package="app.rag", label="retriever"):
    """Maps the `RETRIEVER_PROVIDER` value to the retriever class."""
