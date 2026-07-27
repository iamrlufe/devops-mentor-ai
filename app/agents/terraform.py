from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("terraform")
class TerraformAgent(ConversationalAgent):
    """Terraform and infrastructure as code."""

    name: ClassVar[str] = "terraform"
    description: ClassVar[str] = "Terraform and infrastructure as code"
    capabilities: ClassVar[tuple[str, ...]] = ("terraform", "iac")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("iac", "cloud")
    prompt: ClassVar[str] = "terraform"
