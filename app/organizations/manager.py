from app.config import settings
from app.organizations.factory import OrganizationFactory
from app.organizations.models import Organization, new_organization_id


class OrganizationManager:
    """Reads and creates organizations.

    One organization exists today, and it is created on first use, so nothing
    has to be seeded by hand before the platform can answer.
    """

    @staticmethod
    def default() -> Organization:
        """Return the organization every record belongs to for now."""
        store = OrganizationFactory.create()
        existing = store.get(settings.default_organization_id)

        if existing is not None:
            return existing

        organization = Organization(
            organization_id=settings.default_organization_id,
            name=settings.default_organization_name,
            slug=settings.default_organization_name.lower(),
        )
        store.save(organization)

        return organization

    @staticmethod
    def default_id() -> str:
        """Return the id every record is written with for now."""
        return settings.default_organization_id

    @staticmethod
    def get(organization_id: str) -> Organization | None:
        """Return an organization by id, or `None`."""
        return OrganizationFactory.create().get(organization_id)

    @staticmethod
    def list() -> list[Organization]:
        """Return every organization, the default one included."""
        OrganizationManager.default()

        return OrganizationFactory.create().list()

    @staticmethod
    def create(name: str, plan: str = "default") -> Organization:
        """Create an organization. The platform is ready for more than one."""
        organization = Organization(
            organization_id=new_organization_id(),
            name=name,
            slug=name.lower().replace(" ", "-"),
            plan=plan,
        )
        OrganizationFactory.create().save(organization)

        return organization
