from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("kubernetes")
class KubernetesAgent(ConversationalAgent):
    """Kubernetes workloads and operations."""

    name: ClassVar[str] = "kubernetes"
    description: ClassVar[str] = "Kubernetes workloads and operations"
    capabilities: ClassVar[tuple[str, ...]] = ("kubernetes", "orchestration")
    prompt_file: ClassVar[str] = "kubernetes.md"
