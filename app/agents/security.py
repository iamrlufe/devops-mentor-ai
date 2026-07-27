from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("security")
class SecurityAgent(ConversationalAgent):
    """Infrastructure and application security."""

    name: ClassVar[str] = "security"
    description: ClassVar[str] = "Infrastructure and application security"
    capabilities: ClassVar[tuple[str, ...]] = ("security", "hardening")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("security", "compliance")
    prompt: ClassVar[str] = "security"
