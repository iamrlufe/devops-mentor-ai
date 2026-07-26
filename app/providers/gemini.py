import os

from google import genai
from google.genai import errors

from app.providers.base import BaseProvider


class GeminiProvider(BaseProvider):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Set it in the environment before "
                "starting the application."
            )

        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
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
