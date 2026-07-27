from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("architecture")
class ArchitectureAgent(ConversationalAgent):
    """System design and architecture decisions."""

    name: ClassVar[str] = "architecture"
    description: ClassVar[str] = "System design and architecture decisions"
    capabilities: ClassVar[tuple[str, ...]] = ("design", "architecture")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("design", "planning")
    prompt: ClassVar[str] = "architecture"
