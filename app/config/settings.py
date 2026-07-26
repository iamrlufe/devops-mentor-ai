from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, read from the environment and from `.env`.

    Only the settings of the selected provider have to be filled in. Every
    provider except Gemini is optional, so an unused integration never blocks
    the start of the application.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Which implementation each replaceable layer uses.
    llm_provider: str = "gemini"
    embedding_provider: str = "gemini"
    memory_provider: str = "in_memory"
    retriever_provider: str = "qdrant"
    default_agent: str = "teacher"

    # Gemini: the implemented provider, also used for embeddings.
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"

    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # Claude
    claude_api_key: str | None = None
    claude_model: str = "claude-sonnet-5"

    # Groq
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Ollama, a local runtime that needs no key.
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # OpenRouter
    openrouter_api_key: str | None = None
    openrouter_model: str = "openai/gpt-4o-mini"

    # Azure OpenAI
    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2024-10-21"

    # Embedding providers that are registered but not implemented yet.
    voyageai_api_key: str | None = None
    jina_api_key: str | None = None

    # Vector store
    qdrant_url: str = "http://localhost:6333"

    # Telegram bot
    telegram_token: str | None = None
    api_url: str | None = None


settings = Settings()
