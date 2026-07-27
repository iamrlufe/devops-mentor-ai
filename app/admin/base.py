from abc import ABC, abstractmethod
from typing import Any


class AdminSource(ABC):
    """Where the administration reads its numbers from.

    The service asks this interface, never a database, so a deployment that
    keeps its data somewhere else registers another source and every client —
    REST, Telegram, a web dashboard, a CLI — keeps working unchanged.
    """

    @abstractmethod
    def counters(self) -> dict[str, Any]:
        """Return the platform wide counts."""
        raise NotImplementedError

    @abstractmethod
    def users(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Return profiles with their activity."""
        raise NotImplementedError

    @abstractmethod
    def user_statistics(self, user_id: str) -> dict[str, Any]:
        """Return what one user has produced."""
        raise NotImplementedError

    @abstractmethod
    def user_memory(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Return the memory windows of a user."""
        raise NotImplementedError

    @abstractmethod
    def user_history(self, user_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """Return the newest messages of a user."""
        raise NotImplementedError

    @abstractmethod
    def conversations(
        self,
        user_id: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return conversations, newest first."""
        raise NotImplementedError

    @abstractmethod
    def messages(self, conversation_id: str, limit: int = 200) -> list[dict[str, Any]]:
        """Return the messages of a conversation."""
        raise NotImplementedError

    @abstractmethod
    def registrations(self, days: int = 7) -> list[dict[str, Any]]:
        """Return registrations per day."""
        raise NotImplementedError

    @abstractmethod
    def messages_per_day(self, days: int = 7) -> list[dict[str, Any]]:
        """Return stored messages per day."""
        raise NotImplementedError

    @abstractmethod
    def usage(self, column: str) -> list[dict[str, Any]]:
        """Return request usage grouped by one recorded selection."""
        raise NotImplementedError

    @abstractmethod
    def workspace_selections(self, column: str) -> list[dict[str, Any]]:
        """Return how many workspaces pin each value of one column."""
        raise NotImplementedError

    @abstractmethod
    def agent_usage(self) -> list[dict[str, Any]]:
        """Return users and messages per agent."""
        raise NotImplementedError

    @abstractmethod
    def provider_usage(self) -> list[dict[str, Any]]:
        """Return requests, errors and latency per provider."""
        raise NotImplementedError

    @abstractmethod
    def request_totals(self) -> dict[str, Any]:
        """Return overall request counters and the average response time."""
        raise NotImplementedError
