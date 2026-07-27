from typing import ClassVar

from app.agents.base import DEFAULT_CHAT_ID
from app.agents.conversational import RETRIEVAL_LIMIT, ConversationalAgent
from app.agents.registry import AgentRegistry

__all__ = ["TeacherAgent", "DEFAULT_CHAT_ID", "RETRIEVAL_LIMIT"]


@AgentRegistry.register("teacher")
class TeacherAgent(ConversationalAgent):
    """The DevOps mentor the platform started with: explains step by step and
    ends with an exercise."""

    name: ClassVar[str] = "teacher"
    description: ClassVar[str] = "DevOps mentor for step by step learning"
    capabilities: ClassVar[tuple[str, ...]] = ("learning", "devops", "mentoring")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("learning", "devops")
    prompt: ClassVar[str] = "teacher"
