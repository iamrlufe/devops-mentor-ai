import logging

from app.conversations.manager import ConversationManager
from app.conversations.models import Conversation

logger = logging.getLogger(__name__)

APPROXIMATE_CHARACTERS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Return a rough token count of a text.

    The providers do not all report usage, so the stored number is an estimate
    meant for volume reporting, not for billing.
    """
    return max(1, len(text) // APPROXIMATE_CHARACTERS_PER_TOKEN)


class ConversationService:
    """Records an exchange in the conversation history.

    Recording never breaks answering: if the history cannot be written, the user
    still gets their answer and the failure goes to the log.
    """

    @staticmethod
    def record_exchange(
        chat_id: str,
        agent: str,
        provider: str,
        question: str,
        answer: str,
        user_id: str = "",
    ) -> Conversation | None:
        """Store a question and its answer, creating the conversation if needed.

        Returns:
            The conversation the exchange was written to, or `None` when the
            history could not be written.
        """
        try:
            conversation, created = ConversationManager.ensure(
                chat_id=chat_id,
                agent=agent,
                user_id=user_id,
                provider=provider,
            )

            if created:
                conversation = ConversationManager.set_title(conversation, question)

            ConversationManager.add_message(
                conversation,
                role="user",
                message=question,
                provider=provider,
                tokens=estimate_tokens(question),
            )
            ConversationManager.add_message(
                conversation,
                role="assistant",
                message=answer,
                provider=provider,
                tokens=estimate_tokens(answer),
            )

            return conversation
        except Exception as error:  # noqa: BLE001 - recording must not break the answer
            logger.warning("Could not record the conversation: %s", error)

            return None
