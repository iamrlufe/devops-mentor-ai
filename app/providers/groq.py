from typing import ClassVar

import httpx

from app.config import settings
from app.models.chat_message import ChatMessage
from app.providers.base import BaseProvider
from app.providers.registry import ProviderRegistry

CHAT_COMPLETIONS_PATH = "/chat/completions"
REQUEST_TIMEOUT = 60.0


@ProviderRegistry.register("groq")
class GroqProvider(BaseProvider):
    """Groq through its OpenAI-compatible REST API.

    Groq accepts the `system`, `user` and `assistant` roles as they are, so the
    messages need no translation beyond the shape of the payload. The official
    OpenAI-compatible endpoint is used over httpx, which the project already
    depends on, instead of pulling in another SDK.
    """

    capabilities: ClassVar[tuple[str, ...]] = ("chat", "reasoning", "tool_calling")

    def __init__(self) -> None:
        api_key = settings.groq_api_key

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured. Set it in the environment "
                "before selecting the groq provider."
            )

        self.api_key = api_key
        self.model = settings.groq_model
        self.base_url = settings.groq_base_url.rstrip("/")

    def generate(self, messages: list[ChatMessage]) -> str:
        """Return the answer of the configured Groq model."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
        }

        try:
            response = httpx.post(
                f"{self.base_url}{CHAT_COMPLETIONS_PATH}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPStatusError as error:
            raise RuntimeError(
                f"Groq API request failed ({error.response.status_code}): "
                f"{error.response.text}"
            ) from error
        except httpx.HTTPError as error:
            raise RuntimeError(
                "Could not connect to Groq. Check network access and try again."
            ) from error
        except ValueError as error:
            raise RuntimeError("Groq returned a malformed response.") from error

        return self._extract_answer(body)

    @staticmethod
    def _extract_answer(body: dict) -> str:
        """Pull the answer out of an OpenAI-compatible response.

        Raises:
            RuntimeError: If the response carries no usable answer.
        """
        choices = body.get("choices") or []

        if not choices:
            raise RuntimeError("Groq returned no choices.")

        content = (choices[0].get("message") or {}).get("content")

        if not content:
            raise RuntimeError(
                "Groq returned an empty answer. The request may have been "
                "blocked or the model produced no content."
            )

        return content
