import threading
from typing import ClassVar

from app.config import settings
from app.conversations.base import ConversationStore
from app.conversations.registry import ConversationRegistry
from app.core.instances import get_or_create


class ConversationFactory:
    """Builds the conversation store selected by `CONVERSATION_STORE`.

    The factory knows the registry and nothing else.
    """

    _instances: ClassVar[dict[str, ConversationStore]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    @staticmethod
    def create(name: str = "") -> ConversationStore:
        """Return the conversation store.

        Args:
            name: Which store to build. Empty means the configured one.

        Raises:
            ValueError: If the name is not registered.
        """
        implementation = ConversationRegistry.get(name or settings.conversation_store)
        key = implementation.__name__

        return get_or_create(
            ConversationFactory._instances,
            ConversationFactory._lock,
            key,
            lambda: implementation(),
        )
