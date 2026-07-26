from app.config import settings
from app.providers.gemini import GeminiProvider


class ProviderFactory:

    @staticmethod
    def create():
        provider = settings.llm_provider.lower()

        if provider == "gemini":
            return GeminiProvider()

        raise ValueError(f"Unknown provider: {provider}")
