from app.core.registry import Registry
from app.workspaces.base import WorkspaceStore


class WorkspaceRegistry(
    Registry[WorkspaceStore],
    package="app.workspaces",
    label="workspace store",
):
    """Maps the `WORKSPACE_STORE` value to the store class."""
