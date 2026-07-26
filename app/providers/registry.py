import importlib
import pkgutil
from collections.abc import Callable

from app.providers.base import BaseProvider

# Modules of this package that hold no provider implementation.
INFRASTRUCTURE_MODULES = frozenset({"base", "factory", "registry"})


class ProviderRegistry:
    """Maps a provider name to the class that implements it.

    A provider registers itself with the `register` decorator, and the registry
    finds it by importing every module of the package. Adding a provider is
    therefore a new file with a decorated class and nothing else: no factory,
    no import list and no configuration have to be touched.
    """

    _providers: dict[str, type[BaseProvider]] = {}
    _loaded: bool = False

    @classmethod
    def register(
        cls,
        name: str,
    ) -> Callable[[type[BaseProvider]], type[BaseProvider]]:
        """Return a decorator that registers a provider class under `name`.

        Args:
            name: The value of `LLM_PROVIDER` that selects this provider.

        Raises:
            ValueError: If the name is already taken by another class.
        """

        def decorator(provider: type[BaseProvider]) -> type[BaseProvider]:
            key = cls._normalize(name)
            registered = cls._providers.get(key)

            if registered is not None and registered is not provider:
                raise ValueError(
                    f"Provider '{key}' is already registered by "
                    f"{registered.__name__}."
                )

            cls._providers[key] = provider

            return provider

        return decorator

    @classmethod
    def get(cls, name: str) -> type[BaseProvider]:
        """Return the provider class registered under `name`.

        Raises:
            ValueError: If no provider is registered under that name.
        """
        cls.load_providers()

        provider = cls._providers.get(cls._normalize(name))

        if provider is None:
            raise ValueError(
                f"Unknown provider: '{name}'. Registered providers: "
                f"{', '.join(cls.available())}."
            )

        return provider

    @classmethod
    def available(cls) -> list[str]:
        """Return the names of every registered provider, sorted."""
        cls.load_providers()

        return sorted(cls._providers)

    @classmethod
    def load_providers(cls) -> None:
        """Import the provider modules of this package once, so that the
        `register` decorators run."""
        if cls._loaded:
            return

        cls._loaded = True

        for module in pkgutil.iter_modules(_package_path()):
            if module.name not in INFRASTRUCTURE_MODULES:
                importlib.import_module(f"{__package__}.{module.name}")

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().lower()


def _package_path() -> list[str]:
    """Return the filesystem path of this package."""
    return list(importlib.import_module(__package__).__path__)
