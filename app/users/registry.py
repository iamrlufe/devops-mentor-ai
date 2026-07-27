from app.core.registry import Registry
from app.users.base import UserStore


class UserRegistry(Registry[UserStore], package="app.users", label="user store"):
    """Maps the `USER_STORE` value to the store class."""
