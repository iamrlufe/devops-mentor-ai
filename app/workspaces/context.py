from dataclasses import dataclass

from app.agents.base import BaseAgent
from app.runtime.context import RuntimeContext
from app.workspaces.models import Workspace


@dataclass(frozen=True)
class WorkspaceContext:
    """A workspace resolved into something that can answer.

    It pairs the stored names with the objects they resolved to, so a caller can
    both use the agent and report what the user is actually running on.
    """

    workspace: Workspace
    agent: BaseAgent
    runtime: RuntimeContext

    def ask(self, message: str) -> str:
        """Answer a message in the conversation of this workspace."""
        return self.agent.ask(message, self.workspace.chat_id)

    def describe(self) -> dict[str, str]:
        """Return what the workspace resolved to, including the defaults it
        inherited from the agent and from the platform settings."""
        return {"chat_id": self.workspace.chat_id, **self.runtime.selection}
