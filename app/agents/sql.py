from typing import ClassVar

from app.agents.conversational import ConversationalAgent
from app.agents.registry import AgentRegistry


@AgentRegistry.register("sql")
class SQLAgent(ConversationalAgent):
    """SQL queries, schema design and performance."""

    name: ClassVar[str] = "sql"
    description: ClassVar[str] = "SQL queries, schema design and performance"
    capabilities: ClassVar[tuple[str, ...]] = ("database", "sql")
    prompt_file: ClassVar[str] = "sql.md"
