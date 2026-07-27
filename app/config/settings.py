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
    memory_provider: str = "postgres"
    # Messages kept per chat by the in-process memory. 0 disables the cap.
    memory_max_messages: int = 100
    retriever_provider: str = "qdrant"
    default_agent: str = "teacher"
    # Where the runtime workspaces are kept.
    workspace_store: str = "postgres"
    # Where the user profiles are kept.
    user_store: str = "postgres"
    # Where the conversation history is kept. This is the source of truth.
    conversation_store: str = "postgres"
    # Conversation used when a request names no chat.
    default_chat_id: str = "default"
    # Defaults a profile starts with.
    default_language: str = "ru"
    default_timezone: str = "UTC"

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

    # Vector store. Agents share this collection unless they declare their own.
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "mentor_documents"

    # PostgreSQL. DATABASE_URL wins over the parts when it is set.
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "mentor"
    postgres_user: str = "mentor"
    postgres_password: str = ""
    database_url: str | None = None
    database_pool_min: int = 1
    database_pool_max: int = 10

    # Telegram bot
    telegram_token: str | None = None
    api_url: str | None = None

    @property
    def database_dsn(self) -> str:
        """Return the libpq connection string of the platform database."""
        if self.database_url:
            return self.database_url

        return (
            f"host={self.postgres_host} port={self.postgres_port} "
            f"dbname={self.postgres_db} user={self.postgres_user} "
            f"password={self.postgres_password}"
        )


settings = Settings()
