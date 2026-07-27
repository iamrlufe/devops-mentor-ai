from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException

from app.admin.models import AdminIdentity
from app.admin.permissions import AdminPermissions
from app.admin.service import AdminService

ADMIN_PREFIX = "/admin"
FORBIDDEN = 403
NOT_FOUND = 404

router = APIRouter(prefix=ADMIN_PREFIX, tags=["admin"])


def require_admin(
    x_admin_key: Annotated[str, Header()] = "",
    x_telegram_id: Annotated[str, Header()] = "",
) -> AdminIdentity:
    """Resolve the caller and refuse anyone who is not an administrator.

    The platform decides, not the client: Telegram, a web dashboard and a CLI
    all present the same two headers and are told what they are.

    Raises:
        HTTPException: 403 when no administrator is configured, or the
            credential does not identify one.
    """
    if not AdminPermissions.is_configured():
        raise HTTPException(
            status_code=FORBIDDEN,
            detail=(
                "Administration is disabled: set ADMIN_API_KEY or "
                "ADMIN_TELEGRAM_IDS to enable it."
            ),
        )

    identity = AdminPermissions.identify(x_admin_key, x_telegram_id)

    if not identity.is_admin:
        raise HTTPException(status_code=FORBIDDEN, detail="Administrator only.")

    return identity


#: Every endpoint depends on this, so the check can never be forgotten.
Admin = Annotated[AdminIdentity, Depends(require_admin)]


@router.get("")
def overview(identity: Admin) -> dict[str, object]:
    """Return who the caller is and what the administration offers."""
    return {
        "identity": identity.as_dict(),
        "roles": list(AdminPermissions.roles()),
        "endpoints": [
            "/dashboard",
            "/statistics",
            "/users",
            "/users/{user_id}",
            "/users/{user_id}/profile",
            "/users/{user_id}/workspace",
            "/users/{user_id}/history",
            "/users/{user_id}/memory",
            "/users/{user_id}/statistics",
            "/conversations",
            "/conversations/{conversation_id}",
            "/conversations/{conversation_id}/messages",
            "/agents",
            "/providers",
            "/organizations",
            "/workspaces",
        ],
    }


@router.get("/dashboard")
def dashboard(identity: Admin) -> dict[str, object]:
    """Return the counters an operator sees first."""
    from app.api.routes import VERSION

    return AdminService.dashboard(VERSION)


@router.get("/statistics")
def statistics(
    identity: Admin,
    days: int = 7,
) -> dict[str, object]:
    """Return the breakdowns behind the dashboard."""
    return AdminService.statistics(days)


@router.get("/users")
def users(
    identity: Admin,
    limit: int = 100,
    offset: int = 0,
) -> dict[str, object]:
    """Return the profiles of the platform."""
    return AdminService.users(limit, offset)


@router.get("/users/{user_id}")
def user(
    user_id: str,
    identity: Admin,
) -> dict[str, object]:
    """Return one profile.

    Raises:
        HTTPException: 404 when the profile does not exist.
    """
    return _found(AdminService.user(user_id), user_id)


@router.get("/users/{user_id}/profile")
def user_profile(
    user_id: str,
    identity: Admin,
) -> dict[str, object]:
    """Return one profile.

    Raises:
        HTTPException: 404 when the profile does not exist.
    """
    return _found(AdminService.user(user_id), user_id)


@router.get("/users/{user_id}/workspace")
def user_workspace(
    user_id: str,
    identity: Admin,
) -> dict[str, object]:
    """Return the workspace of a user with what it resolves to."""
    return AdminService.user_workspace(user_id)


@router.get("/users/{user_id}/history")
def user_history(
    user_id: str,
    identity: Admin,
    limit: int = 100,
) -> dict[str, object]:
    """Return the newest messages of a user."""
    return AdminService.user_history(user_id, limit)


@router.get("/users/{user_id}/memory")
def user_memory(
    user_id: str,
    identity: Admin,
    limit: int = 50,
) -> dict[str, object]:
    """Return the memory windows of a user."""
    return AdminService.user_memory(user_id, limit)


@router.get("/users/{user_id}/statistics")
def user_statistics(
    user_id: str,
    identity: Admin,
) -> dict[str, object]:
    """Return what one user has produced."""
    return AdminService.user_statistics(user_id)


@router.get("/conversations")
def conversations(
    identity: Admin,
    user_id: str = "",
    limit: int = 100,
    offset: int = 0,
) -> dict[str, object]:
    """Return conversations, newest first."""
    return AdminService.conversations(user_id, limit, offset)


@router.get("/conversations/{conversation_id}")
def conversation(
    conversation_id: str,
    identity: Admin,
) -> dict[str, object]:
    """Return one conversation.

    Raises:
        HTTPException: 404 when the conversation does not exist.
    """
    return _found(AdminService.conversation(conversation_id), conversation_id)


@router.get("/conversations/{conversation_id}/messages")
def conversation_messages(
    conversation_id: str,
    identity: Admin,
    limit: int = 200,
) -> dict[str, object]:
    """Return the messages of a conversation."""
    return AdminService.messages(conversation_id, limit)


@router.get("/agents")
def agents(identity: Admin) -> dict[str, object]:
    """Return every agent with how much it is used."""
    return AdminService.agents()


@router.get("/providers")
def providers(identity: Admin) -> dict[str, object]:
    """Return every provider with how it has behaved."""
    return AdminService.providers()


@router.get("/organizations")
def organizations(
    identity: Admin,
) -> dict[str, object]:
    """Return every organization."""
    return AdminService.organizations()


@router.get("/workspaces")
def workspaces(
    identity: Admin,
    limit: int = 100,
) -> dict[str, object]:
    """Return the stored workspaces."""
    return AdminService.workspaces(limit)


def _found(value: dict[str, object] | None, identifier: str) -> dict[str, object]:
    """Return the value, or refuse with 404.

    Raises:
        HTTPException: 404 when there is nothing to return.
    """
    if value is None:
        raise HTTPException(
            status_code=NOT_FOUND,
            detail=f"Unknown id: '{identifier}'.",
        )

    return value
