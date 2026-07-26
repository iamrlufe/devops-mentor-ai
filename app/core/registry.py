import importlib
import pkgutil
from collections.abc import Callable
from typing import ClassVar, Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    """Maps a name to the class that implements it, for one kind of component.

    Every replaceable part of the platform — agents, providers, embeddings,
    memory and retrievers — uses this class instead of its own copy of the same
    logic. A subclass only declares which package holds the implementations:

        class ProviderRegistry(Registry[BaseProvider], package="app.providers"):
            pass

    An implementation registers itself with the `register` decorator, and the
    registry finds it by importing the modules of that package. Adding an
    implementation is therefore a new file with a decorated class: no factory,
    no import list and no existing module has to change.
    """

    package: ClassVar[str] = ""
    label: ClassVar[str] = "implementation"

    _entries: ClassVar[dict[str, type]]
    _loaded: ClassVar[bool]

    def __init_subclass__(
        cls,
        package: str = "",
        label: str = "",
        **kwargs: object,
    ) -> None:
        """Give every subclass its own registry state.

        Args:
            package: Import path of the package that holds the implementations.
            label: Human readable name of the component, used in error messages.
        """
        super().__init_subclass__(**kwargs)

        cls._entries = {}
        cls._loaded = False

        if package:
            cls.package = package
        if label:
            cls.label = label

    @classmethod
    def register(cls, name: str) -> Callable[[type[T]], type[T]]:
        """Return a decorator that registers a class under `name`.

        Args:
            name: The configuration value that selects this implementation.

        Raises:
            ValueError: If the name is already taken by a different class.
        """

        def decorator(implementation: type[T]) -> type[T]:
            key = cls._normalize(name)
            registered = cls._entries.get(key)

            if registered is not None and registered is not implementation:
                raise ValueError(
                    f"{cls.label.capitalize()} '{key}' is already registered "
                    f"by {registered.__name__}."
                )

            cls._entries[key] = implementation

            return implementation

        return decorator

    @classmethod
    def get(cls, name: str) -> type[T]:
        """Return the class registered under `name`.

        Raises:
            ValueError: If nothing is registered under that name.
        """
        cls.load()

        implementation = cls._entries.get(cls._normalize(name))

        if implementation is None:
            raise ValueError(
                f"Unknown {cls.label}: '{name}'. "
                f"Registered: {', '.join(cls.available())}."
            )

        return implementation

    @classmethod
    def available(cls) -> list[str]:
        """Return the names of every registered implementation, sorted."""
        cls.load()

        return sorted(cls._entries)

    @classmethod
    def load(cls) -> None:
        """Import the modules of the package once, so the decorators run."""
        if cls._loaded:
            return

        cls._loaded = True
        package = importlib.import_module(cls.package)

        for module in pkgutil.iter_modules(package.__path__):
            importlib.import_module(f"{cls.package}.{module.name}")

    @staticmethod
    def _normalize(name: str) -> str:
        return name.strip().lower()
