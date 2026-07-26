import os

from app.providers.gemini import GeminiProvider


class ProviderFactory:

    @staticmethod
    def create():
        provider = os.getenv("LLM_PROVIDER", "gemini").lower()

        if provider == "gemini":
            return GeminiProvider()

        raise ValueError(f"Unknown provider: {provider}")