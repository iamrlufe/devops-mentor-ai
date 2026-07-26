from app.core.registry import Registry
from app.providers.base import BaseProvider


class ProviderRegistry(
    Registry[BaseProvider],
    package="app.providers",
    label="provider",
):
    """Maps the `LLM_PROVIDER` value to the provider class."""
