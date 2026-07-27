from app.conversations.base import ConversationStore
from app.core.registry import Registry


class ConversationRegistry(
    Registry[ConversationStore],
    package="app.conversations",
    label="conversation store",
):
    """Maps the `CONVERSATION_STORE` value to the store class."""
