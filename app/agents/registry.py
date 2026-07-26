from app.agents.base import BaseAgent
from app.core.registry import Registry

DEFAULT_AGENT = "teacher"


class AgentRegistry(Registry[BaseAgent], package="app.agents", label="agent"):
    """Maps an agent name to the agent class."""
