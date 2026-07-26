from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("docker")
class DockerAgent(ConversationalAgent):
    """Docker images, containers and compose."""

    name: ClassVar[str] = "docker"
    description: ClassVar[str] = "Docker images, containers and compose"
    capabilities: ClassVar[tuple[str, ...]] = ("docker", "containers")
    prompt_file: ClassVar[str] = "docker.md"
