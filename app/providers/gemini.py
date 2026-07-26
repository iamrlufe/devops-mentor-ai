from app.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        return f"Gemini received: {prompt}"