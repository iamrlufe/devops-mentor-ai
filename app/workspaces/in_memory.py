import threading

from app.workspaces.base import WorkspaceStore
from app.workspaces.models import Workspace
from app.workspaces.registry import WorkspaceRegistry


@WorkspaceRegistry.register("in_memory")
class InMemoryWorkspaceStore(WorkspaceStore):
    """Keeps the workspaces in the process memory. They are lost on restart.

    The store is written from the request threadpool and from the bot, so every
    access is guarded.
    """

    def __init__(self) -> None:
        self._workspaces: dict[str, Workspace] = {}
        self._lock = threading.Lock()

    def get(self, chat_id: str) -> Workspace | None:
        with self._lock:
            return self._workspaces.get(chat_id)

    def save(self, workspace: Workspace) -> None:
        with self._lock:
            self._workspaces[workspace.chat_id] = workspace

    def list(self) -> list[Workspace]:
        with self._lock:
            return sorted(self._workspaces.values(), key=lambda item: item.chat_id)

    def delete(self, chat_id: str) -> None:
        with self._lock:
            self._workspaces.pop(chat_id, None)
