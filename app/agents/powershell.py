from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("powershell")
class PowerShellAgent(ConversationalAgent):
    """PowerShell scripting and Windows administration."""

    name: ClassVar[str] = "powershell"
    description: ClassVar[str] = "PowerShell scripting and Windows administration"
    capabilities: ClassVar[tuple[str, ...]] = ("powershell", "windows", "scripting")
    prompt_file: ClassVar[str] = "powershell.md"
