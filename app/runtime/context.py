from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.config import settings
from app.embeddings.base import EmbeddingProvider
from app.embeddings.factory import EmbeddingFactory
from app.memory.base import MemoryProvider
from app.memory.factory import MemoryFactory
from app.prompting.registry import PromptRegistry
from app.providers.base import BaseProvider
from app.providers.factory import ProviderFactory
from app.rag.base import Retriever
from app.rag.factory import RetrieverFactory

if TYPE_CHECKING:  # pragma: no cover - import cycle only exists for type checkers
    from app.agents.base import BaseAgent


@dataclass(frozen=True)
class RuntimeContext:
    """Everything an agent needs to answer, already resolved.

    The agent receives this bundle instead of building anything: it never sees a
    factory, a registry or a setting. What the bundle holds is decided outside
    the agent, which is what lets a workspace run the same agent on another
    provider, memory, retriever or collection without touching agent code.
    """

    prompt: str
    provider: BaseProvider
    memory: MemoryProvider
    retriever: Retriever
    embedding: EmbeddingProvider
    collection: str = ""
    chat_id: str = ""
    #: The names the bundle was resolved from, for reporting and debugging.
    selection: dict[str, str] = field(default_factory=dict)


class RuntimeContextBuilder:
    """Resolves names into a `RuntimeContext`.

    This is the only place that turns configuration into objects. It knows the
    factories; nothing above it does.
    """

    @staticmethod
    def build(
        agent_class: type["BaseAgent"],
        provider: str = "",
        embedding: str = "",
        memory: str = "",
        retriever: str = "",
        collection: str = "",
        prompt: str = "",
        chat_id: str = "",
    ) -> RuntimeContext:
        """Resolve the stack for an agent.

        Every argument is an override. An empty one falls back to what the agent
        declares, and an empty declaration falls back to the platform settings,
        so the three levels compose without any branching on names.

        Args:
            agent_class: The agent whose declared defaults are the middle layer.
            provider: Name of the LLM provider to use.
            embedding: Name of the embedding provider to use.
            memory: Name of the memory provider to use.
            retriever: Name of the retriever to use.
            collection: Collection the retriever searches.
            prompt: Name of the prompt in the `PromptRegistry`.
            chat_id: Conversation the context belongs to.

        Raises:
            ValueError: If a name is not registered.
            FileNotFoundError: If the prompt cannot be resolved.
        """
        provider_name = provider or agent_class.default_provider
        embedding_name = embedding or agent_class.default_embedding
        memory_name = memory or agent_class.default_memory
        retriever_name = retriever or agent_class.default_retriever
        collection_name = collection or agent_class.collection
        prompt_name = prompt or agent_class.prompt

        return RuntimeContext(
            prompt=PromptRegistry.get(prompt_name),
            provider=ProviderFactory.create(provider_name),
            memory=MemoryFactory.create(memory_name),
            retriever=RetrieverFactory.create(
                retriever_name,
                collection_name,
                embedding_name,
            ),
            embedding=EmbeddingFactory.create(embedding_name),
            collection=collection_name,
            chat_id=chat_id or settings.default_chat_id,
            selection={
                "agent": agent_class.name,
                "provider": provider_name or settings.llm_provider,
                "embedding": embedding_name or settings.embedding_provider,
                "memory": memory_name or settings.memory_provider,
                "retriever": retriever_name or settings.retriever_provider,
                "collection": collection_name or settings.qdrant_collection,
                "prompt": prompt_name,
            },
        )
