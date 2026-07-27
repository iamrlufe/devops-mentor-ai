import threading
from typing import ClassVar

from app.config import settings
from app.core.instances import get_or_create
from app.providers.base import BaseProvider
from app.providers.registry import ProviderRegistry


class ProviderFactory:
    """Builds the provider selected by `LLM_PROVIDER`, or the one asked for.

    The factory knows the registry and nothing else: it holds no reference to
    any concrete provider class.
    """

    _instances: ClassVar[dict[str, BaseProvider]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "") -> BaseProvider:
        """Return a provider.

        Args:
            name: Which provider to build. Empty means the one configured by
                `LLM_PROVIDER`, so an agent can declare its own provider without
                any change to the calling code.

        Raises:
            ValueError: If the name is not registered.
        """
        implementation = ProviderRegistry.get(name or settings.llm_provider)
        key = implementation.__name__

        return get_or_create(
            ProviderFactory._instances,
            ProviderFactory._lock,
            key,
            lambda: implementation(),
        )
