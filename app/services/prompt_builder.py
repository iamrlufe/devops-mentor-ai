from app.models.chat_message import ROLE_SYSTEM, ROLE_USER, ChatMessage


class PromptBuilder:

    @staticmethod
    def build(
        system_prompt: str,
        history: list[ChatMessage],
        message: str,
    ) -> list[ChatMessage]:
        """Build the message list for the LLM: system, history, current user message."""
        return [
            ChatMessage(role=ROLE_SYSTEM, content=system_prompt.strip()),
            *history,
            ChatMessage(role=ROLE_USER, content=message),
        ]
