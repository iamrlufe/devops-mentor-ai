from google import genai
from google.genai import errors, types

from app.config import settings
from app.embeddings.base import EmbeddingProvider

BATCH_SIZE = 100
DOCUMENT_TASK_TYPE = "RETRIEVAL_DOCUMENT"
QUERY_TASK_TYPE = "RETRIEVAL_QUERY"


class GeminiEmbeddingProvider(EmbeddingProvider):

    def __init__(self):
        api_key = settings.gemini_api_key
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. Set it in the environment before "
                "starting the application."
            )

        self.model = settings.gemini_embedding_model
        self.client = genai.Client(api_key=api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, DOCUMENT_TASK_TYPE)

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], QUERY_TASK_TYPE)[0]

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        if not texts:
            return []

        if any(not text.strip() for text in texts):
            raise ValueError("Cannot embed an empty text.")

        vectors: list[list[float]] = []
        for start in range(0, len(texts), BATCH_SIZE):
            batch = texts[start:start + BATCH_SIZE]
            vectors.extend(self._embed_batch(batch, task_type))

        return vectors

    def _embed_batch(self, texts: list[str], task_type: str) -> list[list[float]]:
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=texts,
                config=types.EmbedContentConfig(task_type=task_type),
            )
        except errors.APIError as error:
            raise RuntimeError(
                f"Gemini embedding request failed ({error.code}): {error.message}"
            ) from error
        except Exception as error:
            raise RuntimeError(
                "Could not connect to Gemini. Check network access and try again."
            ) from error

        embeddings = response.embeddings or []

        if len(embeddings) != len(texts):
            raise RuntimeError(
                f"Gemini returned {len(embeddings)} embeddings for {len(texts)} texts. "
                "Vectors and chunks would no longer match."
            )

        vectors = []
        for embedding in embeddings:
            if not embedding.values:
                raise RuntimeError("Gemini returned an empty embedding vector.")

            vectors.append(list(embedding.values))

        return vectors
