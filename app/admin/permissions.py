from app.admin.models import ROLE_ADMIN, ROLE_USER, AdminIdentity
from app.config import settings

SOURCE_API_KEY = "api_key"
SOURCE_TELEGRAM = "telegram"


class AdminPermissions:
    """Decides who may read the administration.

    The decision lives in the platform, not in a client: Telegram, a web
    dashboard and a CLI all present a credential and are told what they are.
    """

    @staticmethod
    def identify(api_key: str = "", telegram_id: str = "") -> AdminIdentity:
        """Return the identity behind a credential.

        Args:
            api_key: Value of the admin API key header.
            telegram_id: Telegram account making the request, if any.

        Returns:
            An identity whose role is `admin` only when the credential matches.
        """
        configured = settings.admin_api_key

        if configured and api_key and api_key == configured:
            return AdminIdentity(
                role=settings.admin_role,
                subject=SOURCE_API_KEY,
                source=SOURCE_API_KEY,
            )

        if telegram_id and telegram_id in settings.admin_telegram_id_set:
            return AdminIdentity(
                role=settings.admin_role,
                subject=telegram_id,
                source=SOURCE_TELEGRAM,
            )

        return AdminIdentity(role=ROLE_USER, subject=telegram_id, source="")

    @staticmethod
    def is_configured() -> bool:
        """Whether any administrator can exist at all."""
        return bool(settings.admin_api_key or settings.admin_telegram_id_set)

    @staticmethod
    def roles() -> tuple[str, ...]:
        """Return the roles the platform knows."""
        return (ROLE_ADMIN, ROLE_USER)
