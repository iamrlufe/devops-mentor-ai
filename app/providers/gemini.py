from google import genai
from google.genai import errors, types

from app.config import settings
from app.models.chat_message import (
    ROLE_ASSISTANT,
    ROLE_SYSTEM,
    ROLE_USER,
    ChatMessage,
)
from app.providers.base import BaseProvider

GEMINI_ROLES = {
    ROLE_USER: "user",
    ROLE_ASSISTANT: "model",
}


class GeminiProvider(BaseProvider):

    def __init__(self):
        api_key = settings.gemini_api_key
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Set it in the environment before "
                "starting the application."
            )

        self.model = settings.gemini_model
        self.client = genai.Client(api_key=api_key)

    def generate(self, messages: list[ChatMessage]) -> str:
        system_instruction, contents = self._to_gemini_format(messages)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction or None,
                ),
            )
        except errors.APIError as error:
            raise RuntimeError(
                f"Gemini API request failed ({error.code}): {error.message}"
            ) from error
        except Exception as error:
            raise RuntimeError(
                "Could not connect to Gemini. Check network access and try again."
            ) from error

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response. The prompt may have been blocked "
                "by safety filters."
            )

        return response.text

    @staticmethod
    def _to_gemini_format(
        messages: list[ChatMessage],
    ) -> tuple[str, list[types.Content]]:
        """Split the messages into a system instruction and Gemini contents."""
        system_parts: list[str] = []
        contents: list[types.Content] = []

        for message in messages:
            if message.role == ROLE_SYSTEM:
                system_parts.append(message.content)
                continue

            role = GEMINI_ROLES.get(message.role)
            if role is None:
                raise ValueError(f"Unsupported message role: {message.role}")

            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=message.content)],
                )
            )

        if not contents:
            raise ValueError("Gemini requires at least one user or assistant message.")

        return "\n\n".join(system_parts), contents
