from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("docker")
class DockerAgent(ConversationalAgent):
    """Docker images, containers and compose."""

    name: ClassVar[str] = "docker"
    description: ClassVar[str] = "Docker images, containers and compose"
    capabilities: ClassVar[tuple[str, ...]] = ("docker", "containers")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("containers", "build")
    prompt: ClassVar[str] = "docker"
