from app.agents.base import BaseAgent
from app.core.registry import Registry


class AgentRegistry(Registry[BaseAgent], package="app.agents", label="agent"):
    """Maps an agent name to the agent class."""
