from app.agents.base import BaseAgent
from app.agents.registry import DEFAULT_AGENT, AgentRegistry


class AgentFactory:
    """Builds agents by name.

    The factory knows the registry and nothing else: it holds no reference to
    any concrete agent class. Instances are reused, because building an agent
    also builds its provider, memory and retriever.
    """

    _instances: dict[str, BaseAgent] = {}

    @staticmethod
    def create(name: str = DEFAULT_AGENT) -> BaseAgent:
        """Return the agent registered under `name`.

        Args:
            name: The agent to build. Defaults to the teacher, which keeps the
                behaviour of the single agent the platform started with.

        Raises:
            ValueError: If no agent is registered under that name.
        """
        agent_class = AgentRegistry.get(name)
        key = agent_class.name or name

        if key not in AgentFactory._instances:
            AgentFactory._instances[key] = agent_class()

        return AgentFactory._instances[key]
