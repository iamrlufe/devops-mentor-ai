from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("codereview")
class CodeReviewAgent(ConversationalAgent):
    """Code review for correctness and maintainability."""

    name: ClassVar[str] = "codereview"
    description: ClassVar[str] = "Code review for correctness and maintainability"
    capabilities: ClassVar[tuple[str, ...]] = ("review", "code_quality")
    prompt_file: ClassVar[str] = "codereview.md"
