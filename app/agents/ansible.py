from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("ansible")
class AnsibleAgent(ConversationalAgent):
    """Ansible playbooks and configuration management."""

    name: ClassVar[str] = "ansible"
    description: ClassVar[str] = "Ansible playbooks and configuration management"
    capabilities: ClassVar[tuple[str, ...]] = ("ansible", "configuration_management")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("iac", "configuration")
    prompt: ClassVar[str] = "ansible"
