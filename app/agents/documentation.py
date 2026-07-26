from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("documentation")
class DocumentationAgent(ConversationalAgent):
    """Technical writing: READMEs, runbooks, API docs."""

    name: ClassVar[str] = "documentation"
    description: ClassVar[str] = "Technical writing: READMEs, runbooks, API docs"
    capabilities: ClassVar[tuple[str, ...]] = ("documentation", "writing")
    prompt_file: ClassVar[str] = "documentation.md"
