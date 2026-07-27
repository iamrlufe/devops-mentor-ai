from abc import ABC, abstractmethod

from app.workspaces.models import Workspace


class WorkspaceStore(ABC):
    """Where workspaces live.

    The in-process store ships with the platform; a persistent one is a new
    class registered under a new name, with nothing else to change.
    """

    @abstractmethod
    def get(self, chat_id: str) -> Workspace | None:
        """Return the stored workspace of a chat, or `None`."""
        raise NotImplementedError

    @abstractmethod
    def save(self, workspace: Workspace) -> None:
        """Store a workspace, replacing the one with the same chat id."""
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Workspace]:
        """Return every stored workspace."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, chat_id: str) -> None:
        """Forget the workspace of a chat. Missing chats are ignored."""
        raise NotImplementedError
