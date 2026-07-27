from app.conversations.factory import ConversationFactory
from app.conversations.models import (
    Conversation,
    ConversationMessage,
    new_conversation_id,
)
from app.organizations.manager import OrganizationManager

TITLE_LENGTH = 60


class ConversationManager:
    """Finds and updates conversations.

    One conversation per chat and agent: switching the agent starts a new
    thread, which is what keeps two agents in the same chat from sharing a
    history.
    """

    @staticmethod
    def ensure(
        chat_id: str,
        agent: str,
        user_id: str = "",
        provider: str = "",
    ) -> tuple[Conversation, bool]:
        """Return the conversation of a chat with an agent, creating it once.

        Returns:
            The conversation and whether this call created it.
        """
        store = ConversationFactory.create()
        existing = store.find(chat_id, agent)

        if existing is not None:
            return existing, False

        conversation = Conversation(
            conversation_id=new_conversation_id(),
            organization_id=OrganizationManager.default_id(),
            user_id=user_id,
            chat_id=chat_id,
            agent=agent,
            provider=provider,
        )
        store.save(conversation)

        return conversation, True

    @staticmethod
    def add_message(
        conversation: Conversation,
        role: str,
        message: str,
        provider: str = "",
        tokens: int = 0,
        metadata: dict[str, str] | None = None,
    ) -> ConversationMessage:
        """Append a message to a conversation."""
        return ConversationFactory.create().add_message(
            ConversationMessage(
                conversation_id=conversation.conversation_id,
                organization_id=conversation.organization_id,
                user_id=conversation.user_id,
                agent=conversation.agent,
                provider=provider or conversation.provider,
                role=role,
                message=message,
                tokens=tokens,
                metadata=metadata or {},
            )
        )

    @staticmethod
    def messages(conversation_id: str, limit: int = 0) -> list[ConversationMessage]:
        """Return the stored messages of a conversation, oldest first."""
        return ConversationFactory.create().messages(conversation_id, limit)

    @staticmethod
    def list_for_user(user_id: str) -> list[Conversation]:
        """Return the conversations of a user, newest first."""
        return ConversationFactory.create().list_for_user(user_id)

    @staticmethod
    def set_title(conversation: Conversation, title: str) -> Conversation:
        """Give a conversation a title, shortened to fit."""
        updated = conversation.with_changes(title=title[:TITLE_LENGTH])
        ConversationFactory.create().save(updated)

        return updated
