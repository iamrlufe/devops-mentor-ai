from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("ansible")
class AnsibleAgent(ConversationalAgent):
    """Ansible playbooks and configuration management."""

    name: ClassVar[str] = "ansible"
    description: ClassVar[str] = "Ansible playbooks and configuration management"
    capabilities: ClassVar[tuple[str, ...]] = ("ansible", "configuration_management")
    prompt_file: ClassVar[str] = "ansible.md"
