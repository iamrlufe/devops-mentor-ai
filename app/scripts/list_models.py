from google import genai

from app.config import settings

if not settings.gemini_api_key:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=settings.gemini_api_key)

for model in client.models.list():
    print(model.name)
