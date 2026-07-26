from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("linux")
class LinuxAgent(ConversationalAgent):
    """Linux administration and shell."""

    name: ClassVar[str] = "linux"
    description: ClassVar[str] = "Linux administration and shell"
    capabilities: ClassVar[tuple[str, ...]] = ("linux", "shell", "administration")
    prompt_file: ClassVar[str] = "linux.md"
