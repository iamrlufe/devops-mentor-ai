import threading

from app.organizations.base import OrganizationStore
from app.organizations.models import Organization
from app.organizations.registry import OrganizationRegistry


@OrganizationRegistry.register("in_memory")
class InMemoryOrganizationStore(OrganizationStore):
    """Demo store: keeps the organizations in the process memory."""

    def __init__(self) -> None:
        self._organizations: dict[str, Organization] = {}
        self._lock = threading.Lock()

    def get(self, organization_id: str) -> Organization | None:
        with self._lock:
            return self._organizations.get(organization_id)

    def save(self, organization: Organization) -> None:
        with self._lock:
            self._organizations[organization.organization_id] = organization

    def list(self) -> list[Organization]:
        with self._lock:
            return sorted(
                self._organizations.values(), key=lambda item: item.created_at
            )

    def delete(self, organization_id: str) -> None:
        with self._lock:
            self._organizations.pop(organization_id, None)
