from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("kubernetes")
class KubernetesAgent(ConversationalAgent):
    """Kubernetes workloads and operations."""

    name: ClassVar[str] = "kubernetes"
    description: ClassVar[str] = "Kubernetes workloads and operations"
    capabilities: ClassVar[tuple[str, ...]] = ("kubernetes", "orchestration")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("containers", "orchestration")
    prompt: ClassVar[str] = "kubernetes"
