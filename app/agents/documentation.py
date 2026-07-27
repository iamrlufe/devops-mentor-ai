from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("documentation")
class DocumentationAgent(ConversationalAgent):
    """Technical writing: READMEs, runbooks, API docs."""

    name: ClassVar[str] = "documentation"
    description: ClassVar[str] = "Technical writing: READMEs, runbooks, API docs"
    capabilities: ClassVar[tuple[str, ...]] = ("documentation", "writing")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("writing", "docs")
    prompt: ClassVar[str] = "documentation"
