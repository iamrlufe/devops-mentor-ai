import threading
from typing import ClassVar

from app.agents.base import BaseAgent
from app.agents.registry import AgentRegistry
from app.config import settings
from app.core.instances import get_or_create


class AgentFactory:
    """Builds agents by name.

    The factory knows the registry and nothing else: it holds no reference to
    any concrete agent class. Instances are reused, because building an agent
    also builds its provider, memory and retriever.
    """

    _instances: ClassVar[dict[str, BaseAgent]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "") -> BaseAgent:
        """Return the agent registered under `name`.

        Args:
            name: The agent to build. Empty means the agent configured by
                `DEFAULT_AGENT`, which is what keeps requests without an agent
                field working exactly as before.

        Raises:
            ValueError: If no agent is registered under that name.
        """
        agent_class = AgentRegistry.get(name or settings.default_agent)
        key = agent_class.name or agent_class.__name__

        return get_or_create(
            AgentFactory._instances,
            AgentFactory._lock,
            key,
            lambda: agent_class(),
        )
