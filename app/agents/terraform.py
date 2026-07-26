from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("terraform")
class TerraformAgent(ConversationalAgent):
    """Terraform and infrastructure as code."""

    name: ClassVar[str] = "terraform"
    description: ClassVar[str] = "Terraform and infrastructure as code"
    capabilities: ClassVar[tuple[str, ...]] = ("terraform", "iac")
    prompt_file: ClassVar[str] = "terraform.md"
