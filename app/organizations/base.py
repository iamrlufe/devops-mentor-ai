from abc import ABC, abstractmethod

from app.organizations.models import Organization


class OrganizationStore(ABC):
    """Where organizations live."""

    @abstractmethod
    def get(self, organization_id: str) -> Organization | None:
        """Return an organization by id, or `None`."""
        raise NotImplementedError

    @abstractmethod
    def save(self, organization: Organization) -> None:
        """Store an organization, replacing the one with the same id."""
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Organization]:
        """Return every organization."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, organization_id: str) -> None:
        """Remove an organization. Missing ids are ignored."""
        raise NotImplementedError
