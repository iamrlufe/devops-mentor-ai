from app.config import settings
from app.providers.base import BaseProvider
from app.providers.registry import ProviderRegistry


class ProviderFactory:
    """Builds the provider selected by the `LLM_PROVIDER` setting.

    The factory knows the registry and nothing else: it holds no reference to
    any concrete provider class.
    """

    @staticmethod
    def create() -> BaseProvider:
        """Return a new instance of the configured provider.

        Raises:
            ValueError: If `LLM_PROVIDER` names a provider that is not
                registered.
        """
        return ProviderRegistry.get(settings.llm_provider)()
