from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("linux")
class LinuxAgent(ConversationalAgent):
    """Linux administration and shell."""

    name: ClassVar[str] = "linux"
    description: ClassVar[str] = "Linux administration and shell"
    capabilities: ClassVar[tuple[str, ...]] = ("linux", "shell", "administration")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("linux", "operations")
    prompt: ClassVar[str] = "linux"
