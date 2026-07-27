from typing import Any

from app.admin.factory import AdminFactory
from app.agents.registry import AgentRegistry
from app.embeddings.registry import EmbeddingRegistry
from app.memory.registry import MemoryRegistry
from app.providers.registry import ProviderRegistry
from app.rag.registry import RetrieverRegistry
from app.users.manager import UserManager
from app.vectorstore.factory import VectorStoreFactory
from app.workspaces.manager import WorkspaceManager


class AdminManager:
    """Reads the platform on behalf of an administrator.

    The manager joins what the registries already know with what the source
    counted, so no client has to know either.
    """

    @staticmethod
    def registry_sizes() -> dict[str, int]:
        """Return how many implementations each registry holds."""
        return {
            "agents_total": len(AgentRegistry.available()),
            "providers_total": len(ProviderRegistry.available()),
            "embedding_providers_total": len(EmbeddingRegistry.available()),
            "memory_providers_total": len(MemoryRegistry.available()),
            "retrievers_total": len(RetrieverRegistry.available()),
        }

    @staticmethod
    def vector_store_counts() -> dict[str, int]:
        """Return how many documents and collections the vector store holds.

        A vector store that cannot be reached reports zero rather than breaking
        the dashboard.
        """
        try:
            store = VectorStoreFactory.create()
            collections = store.client.get_collections().collections
            documents = 0

            for collection in collections:
                documents += store.client.count(collection.name).count

            return {
                "documents_total": documents,
                "collections_total": len(collections),
            }
        except Exception:  # noqa: BLE001 - the dashboard reports, never breaks
            return {"documents_total": 0, "collections_total": 0}

    @staticmethod
    def users(limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Return profiles with their activity."""
        return AdminFactory.create().users(limit, offset)

    @staticmethod
    def user(user_id: str) -> dict[str, Any] | None:
        """Return one profile as plain data, or `None`."""
        profile = UserManager.get(user_id)

        return profile.as_dict() if profile else None

    @staticmethod
    def workspace(user_id: str) -> dict[str, Any]:
        """Return the workspace of a user with what it resolves to."""
        stored = WorkspaceManager.get(user_id)

        try:
            resolved = WorkspaceManager.resolve(user_id).describe()
        except (ValueError, FileNotFoundError) as error:
            resolved = {"error": str(error)}

        return {"workspace": stored.as_dict(), "resolved": resolved}

    @staticmethod
    def agents() -> list[dict[str, Any]]:
        """Return every agent with how much it is used."""
        source = AdminFactory.create()
        usage = {row["agent"]: row for row in source.agent_usage()}
        agents = []

        for name in AgentRegistry.available():
            metadata = AgentRegistry.get(name).metadata()
            counted = usage.get(name, {})

            agents.append(
                {
                    "agent": name,
                    "description": metadata["description"],
                    "users": counted.get("users", 0),
                    "messages": counted.get("messages", 0),
                    "provider": metadata["provider"],
                    "embedding": metadata["embedding"],
                    "memory": metadata["memory"],
                    "retriever": metadata["retriever"],
                    "collection": metadata["collection"],
                }
            )

        return agents

    @staticmethod
    def providers() -> list[dict[str, Any]]:
        """Return every provider with how it has behaved."""
        source = AdminFactory.create()
        usage = {row["provider"]: row for row in source.provider_usage()}
        providers = []

        for name in ProviderRegistry.available():
            metadata = ProviderRegistry.get(name).metadata()
            counted = usage.get(name, {})

            providers.append(
                {
                    "provider": name,
                    "implemented": metadata["implemented"],
                    "requests": counted.get("requests", 0),
                    "errors": counted.get("errors", 0),
                    "average_latency": int(counted.get("average_latency_ms", 0) or 0),
                    "users": counted.get("users", 0),
                }
            )

        return providers
