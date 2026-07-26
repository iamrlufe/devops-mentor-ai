from app.models.chat_message import ROLE_SYSTEM, ROLE_USER, ChatMessage

CONTEXT_INSTRUCTION = (
    "Use the documentation below when it answers the question. "
    "Name the source you relied on. Ignore it when it is not relevant."
)


class PromptBuilder:

    @staticmethod
    def build(
        system_prompt: str,
        history: list[ChatMessage],
        message: str,
        context: str = "",
    ) -> list[ChatMessage]:
        """Build the message list for the LLM: system prompt, retrieved context,
        history, current user message."""
        messages = [ChatMessage(role=ROLE_SYSTEM, content=system_prompt.strip())]

        if context.strip():
            messages.append(
                ChatMessage(
                    role=ROLE_SYSTEM,
                    content=f"{CONTEXT_INSTRUCTION}\n\n{context.strip()}",
                )
            )

        messages.extend(history)
        messages.append(ChatMessage(role=ROLE_USER, content=message))

        return messages
