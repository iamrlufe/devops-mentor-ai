from app.agents.registry import AgentRegistry
from app.config import settings
from app.core.registry import Registry
from app.embeddings.registry import EmbeddingRegistry
from app.memory.registry import MemoryRegistry
from app.prompting.registry import PromptRegistry
from app.providers.registry import ProviderRegistry
from app.rag.registry import RetrieverRegistry
from app.runtime.context import RuntimeContextBuilder
from app.workspaces.context import WorkspaceContext
from app.workspaces.factory import WorkspaceFactory
from app.workspaces.models import Workspace

#: Which registry validates which workspace field. Data, not branching: a new
#: replaceable layer is one more entry, and a new implementation is none.
FIELD_REGISTRIES: dict[str, type[Registry]] = {
    "agent": AgentRegistry,
    "provider": ProviderRegistry,
    "embedding": EmbeddingRegistry,
    "memory": MemoryRegistry,
    "retriever": RetrieverRegistry,
}


class WorkspaceManager:
    """Reads and updates the workspace of a chat, and resolves it into an agent.

    Every user works in their own workspace, so switching an agent or a provider
    changes that user only. Names are validated when they are set, which keeps a
    workspace from ever pointing at something that does not exist.
    """

    @staticmethod
    def get(chat_id: str = "") -> Workspace:
        """Return the workspace of a chat, creating an empty one on first use."""
        key = chat_id or settings.default_chat_id
        stored = WorkspaceFactory.create().get(key)

        return stored if stored is not None else Workspace(chat_id=key)

    @staticmethod
    def list() -> list[Workspace]:
        """Return every workspace that has been touched."""
        return WorkspaceFactory.create().list()

    @staticmethod
    def update(chat_id: str = "", **changes: str) -> Workspace:
        """Change part of a workspace and store it.

        Args:
            chat_id: Whose workspace to change.
            **changes: Any mutable workspace field. Empty strings reset a field
                back to the platform default.

        Returns:
            The stored workspace.

        Raises:
            ValueError: If a field is unknown, a name is not registered, or the
                chosen provider is not implemented yet.
        """
        updated = WorkspaceManager.get(chat_id).with_changes(**changes)

        WorkspaceManager._validate(updated)
        WorkspaceFactory.create().save(updated)

        return updated

    @staticmethod
    def resolve(chat_id: str = "", agent: str = "") -> WorkspaceContext:
        """Build everything the workspace needs to answer.

        Args:
            chat_id: Whose workspace to resolve.
            agent: Agent for this one request, overriding the workspace without
                changing it. Empty uses the workspace agent.

        Raises:
            ValueError: If a name is not registered.
        """
        workspace = WorkspaceManager.get(chat_id)
        agent_name = agent or workspace.agent or settings.default_agent
        agent_class = AgentRegistry.get(agent_name)

        runtime = RuntimeContextBuilder.build(
            agent_class,
            provider=workspace.provider,
            embedding=workspace.embedding,
            memory=workspace.memory,
            retriever=workspace.retriever,
            collection=workspace.collection,
            prompt=workspace.prompt,
            chat_id=workspace.chat_id,
        )

        return WorkspaceContext(
            workspace=workspace,
            agent=agent_class(runtime),
            runtime=runtime,
        )

    @staticmethod
    def _validate(workspace: Workspace) -> None:
        """Check every name the workspace points at.

        Raises:
            ValueError: If a name is not registered, or the provider is
                registered but not implemented yet.
        """
        for field, registry in FIELD_REGISTRIES.items():
            name = getattr(workspace, field)

            if name:
                registry.get(name)

        if workspace.prompt:
            PromptRegistry.get(workspace.prompt)

        if workspace.provider:
            provider = ProviderRegistry.get(workspace.provider)

            if not provider.implemented:
                implemented = sorted(
                    name
                    for name in ProviderRegistry.available()
                    if ProviderRegistry.get(name).implemented
                )
                raise ValueError(
                    f"Provider '{workspace.provider}' is registered but not "
                    f"implemented yet. Implemented providers: "
                    f"{', '.join(implemented)}."
                )
