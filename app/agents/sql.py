from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("sql")
class SQLAgent(ConversationalAgent):
    """SQL queries, schema design and performance."""

    name: ClassVar[str] = "sql"
    description: ClassVar[str] = "SQL queries, schema design and performance"
    capabilities: ClassVar[tuple[str, ...]] = ("database", "sql")
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("database", "performance")
    prompt: ClassVar[str] = "sql"
