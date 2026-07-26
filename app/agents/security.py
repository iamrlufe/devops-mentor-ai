from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("security")
class SecurityAgent(ConversationalAgent):
    """Infrastructure and application security."""

    name: ClassVar[str] = "security"
    description: ClassVar[str] = "Infrastructure and application security"
    capabilities: ClassVar[tuple[str, ...]] = ("security", "hardening")
    prompt_file: ClassVar[str] = "security.md"
