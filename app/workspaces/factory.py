import threading
from typing import ClassVar

from app.config import settings
from app.core.instances import get_or_create
from app.workspaces.base import WorkspaceStore
from app.workspaces.registry import WorkspaceRegistry


class WorkspaceFactory:
    """Builds the workspace store selected by `WORKSPACE_STORE`.

    The factory knows the registry and nothing else. One instance is shared for
    the whole process, which is what makes a workspace visible to every request
    of the same user.
    """

    _instances: ClassVar[dict[str, WorkspaceStore]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "") -> WorkspaceStore:
        """Return the workspace store.

        Args:
            name: Which store to build. Empty means the configured one.

        Raises:
            ValueError: If the name is not registered.
        """
        implementation = WorkspaceRegistry.get(name or settings.workspace_store)
        key = implementation.__name__

        return get_or_create(
            WorkspaceFactory._instances,
            WorkspaceFactory._lock,
            key,
            lambda: implementation(),
        )
