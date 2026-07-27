import uuid
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime

ORGANIZATION_ID_PREFIX = "org_"
ORGANIZATION_ID_LENGTH = 12

MUTABLE_FIELDS = ("name", "slug", "plan", "is_active", "metadata")


def new_organization_id() -> str:
    """Return a fresh organization id, for example `org_2f9c1d40ab77`."""
    return f"{ORGANIZATION_ID_PREFIX}{uuid.uuid4().hex[:ORGANIZATION_ID_LENGTH]}"


def now() -> datetime:
    """Return the current moment in UTC."""
    return datetime.now(UTC)


@dataclass(frozen=True)
class Organization:
    """A tenant of the platform.

    Everything a user creates belongs to one, so the day a second organization
    appears no table has to change.
    """

    organization_id: str
    name: str = ""
    slug: str = ""
    plan: str = "default"
    is_active: bool = True
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)

    def with_changes(self, **changes: object) -> "Organization":
        """Return a copy with the given fields replaced.

        Raises:
            ValueError: If a field is not one a caller may change.
        """
        applied = {}

        for name, value in changes.items():
            if value is None:
                continue
            if name not in MUTABLE_FIELDS:
                raise ValueError(
                    f"Unknown organization field: '{name}'. "
                    f"Known fields: {', '.join(MUTABLE_FIELDS)}."
                )
            applied[name] = value

        return replace(self, updated_at=now(), **applied)

    def as_dict(self) -> dict[str, object]:
        """Return the organization as plain data."""
        return {
            "organization_id": self.organization_id,
            "name": self.name,
            "slug": self.slug,
            "plan": self.plan,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(timespec="seconds"),
            "updated_at": self.updated_at.isoformat(timespec="seconds"),
        }
