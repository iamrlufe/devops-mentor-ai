from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("infrastructure")
class InfrastructureAgent(ConversationalAgent):
    """Infrastructure design and operations."""

    name: ClassVar[str] = "infrastructure"
    description: ClassVar[str] = "Infrastructure design and operations"
    capabilities: ClassVar[tuple[str, ...]] = ("infrastructure", "devops")
    prompt_file: ClassVar[str] = "infrastructure.md"
