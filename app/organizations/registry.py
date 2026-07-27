from app.core.registry import Registry
from app.organizations.base import OrganizationStore


class OrganizationRegistry(
    Registry[OrganizationStore],
    package="app.organizations",
    label="organization store",
):
    """Maps the `ORGANIZATION_STORE` value to the store class."""
