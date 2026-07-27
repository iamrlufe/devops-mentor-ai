from app.admin.base import AdminSource
from app.core.registry import Registry


class AdminRegistry(Registry[AdminSource], package="app.admin", label="admin source"):
    """Maps the `ADMIN_SOURCE` value to the source class."""
