from typing import Any

from app.database.repositories.workspace_repository import WorkspaceRepository
from app.workspaces.base import WorkspaceStore
from app.workspaces.models import Workspace
from app.workspaces.registry import WorkspaceRegistry


def to_workspace(row: dict[str, Any]) -> Workspace:
    """Turn a database row into a workspace."""
    return Workspace(
        chat_id=row["chat_id"],
        user_id=row["user_id"],
        agent=row["agent"],
        provider=row["provider"],
        embedding=row["embedding"],
        memory=row["memory"],
        retriever=row["retriever"],
        collection=row["collection"],
        prompt=row["prompt"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def to_row(workspace: Workspace) -> dict[str, Any]:
    """Turn a workspace into the values the repository expects."""
    return {
        "chat_id": workspace.chat_id,
        "user_id": workspace.user_id,
        "agent": workspace.agent,
        "provider": workspace.provider,
        "embedding": workspace.embedding,
        "memory": workspace.memory,
        "retriever": workspace.retriever,
        "collection": workspace.collection,
        "prompt": workspace.prompt,
        "created_at": workspace.created_at,
        "updated_at": workspace.updated_at,
    }


@WorkspaceRegistry.register("postgres")
class PostgresWorkspaceStore(WorkspaceStore):
    """Keeps the workspaces in PostgreSQL, so a restart does not reset them."""

    def get(self, chat_id: str) -> Workspace | None:
        row = WorkspaceRepository.get(chat_id)

        return to_workspace(row) if row else None

    def save(self, workspace: Workspace) -> None:
        WorkspaceRepository.upsert(to_row(workspace))

    def list(self) -> list[Workspace]:
        return [to_workspace(row) for row in WorkspaceRepository.list()]

    def delete(self, chat_id: str) -> None:
        WorkspaceRepository.delete(chat_id)
