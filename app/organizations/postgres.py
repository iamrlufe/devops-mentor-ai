from typing import Any

from app.organizations.base import OrganizationStore
from app.organizations.models import Organization
from app.organizations.registry import OrganizationRegistry
from app.organizations.repository import OrganizationRepository


def to_organization(row: dict[str, Any]) -> Organization:
    """Turn a database row into an organization."""
    return Organization(
        organization_id=row["organization_id"],
        name=row["name"],
        slug=row["slug"],
        plan=row["plan"],
        is_active=row["is_active"],
        metadata=dict(row["metadata"] or {}),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@OrganizationRegistry.register("postgres")
class PostgresOrganizationStore(OrganizationStore):
    """Keeps the organizations in PostgreSQL."""

    def get(self, organization_id: str) -> Organization | None:
        row = OrganizationRepository.get(organization_id)

        return to_organization(row) if row else None

    def save(self, organization: Organization) -> None:
        OrganizationRepository.upsert(
            {
                "organization_id": organization.organization_id,
                "name": organization.name,
                "slug": organization.slug,
                "plan": organization.plan,
                "is_active": organization.is_active,
                "metadata": organization.metadata,
                "created_at": organization.created_at,
                "updated_at": organization.updated_at,
            }
        )

    def list(self) -> list[Organization]:
        return [to_organization(row) for row in OrganizationRepository.list()]

    def delete(self, organization_id: str) -> None:
        OrganizationRepository.delete(organization_id)
