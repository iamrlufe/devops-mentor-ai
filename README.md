# DevOps Mentor AI

An AI assistant framework for learning, DevOps and system administration.

The project is built as a set of replaceable layers rather than a wrapper around
one vendor. Every external dependency — the LLM, the embedding model, the vector
store, the conversation memory — sits behind an interface and is created through
a factory, so a new provider is a new class, not a rewrite. Gemini is the
provider implemented today; the architecture is not tied to it.

The assistant answers questions with retrieval-augmented generation: your
markdown documentation is indexed into a vector store, the relevant pieces are
found for each question and passed to the model as context.

## Features

- **REST API** — FastAPI service with `/chat`, `/health` and OpenAPI docs.
- **Telegram Bot** — long-polling bot that talks to the same API.
- **RAG** — retrieved documentation is injected into the prompt as a separate
  system message, so answers stay grounded in your own docs.
- **Vector Search** — semantic search over Qdrant with cosine distance.
- **Conversation Memory** — per-chat history behind a `MemoryProvider`
  interface; the in-process implementation ships by default.
- **Prompt System** — the system prompt lives in `app/prompts/teacher.md`, and
  `PromptBuilder` assembles system prompt, context, history and question into a
  provider-independent message list.
- **Document Indexing** — one command turns a directory of markdown into a
  searchable index: load, chunk, embed, upload.
- **Multiple LLM Providers** — a registry maps `LLM_PROVIDER` to a provider
  class; seven are registered and a new one is a single new file.
- **Docker Deployment** — the whole stack starts with a single compose command.

## Architecture

```
User
  │
Telegram Bot / REST API
  │
Teacher Agent ────────── Conversation Memory
  │
Prompt Builder
  │
Retriever
  │
Qdrant (vector search)
  │
LLM Provider
  │
Gemini / OpenAI / Claude / Ollama   (architecture allows adding new ones)
```

A question travels through the agent like this:

1. `TeacherAgent` loads the conversation history for the chat.
2. The retriever embeds the question and searches Qdrant for the five closest
   chunks.
3. `ContextBuilder` renders them into a context block.
4. `PromptBuilder` assembles the messages: system prompt → retrieved context →
   history → question.
5. The provider translates that list into its own API format and returns the
   answer, which is then saved to memory.

If the index is missing or the search fails, the agent logs a warning and
answers without context instead of failing the request.

The indexing pipeline is separate and runs on demand:

```
docs/*.md → DocumentLoader → Chunker → Embeddings → Qdrant
```

## Project Structure

```
devops-mentor-ai/
├── app/
│   ├── agents/
│   │   └── teacher.py            # TeacherAgent: memory + retrieval + prompt + provider
│   ├── chunking/                 # splitting documents into overlapping chunks
│   │   ├── base.py               # Chunker interface
│   │   ├── factory.py
│   │   ├── markdown_chunker.py   # 1000 characters, 200 overlap
│   │   ├── models.py             # Chunk
│   │   └── service.py            # ChunkService
│   ├── config/
│   │   └── settings.py           # pydantic-settings, reads .env
│   ├── documents/                # reading documents from disk
│   │   ├── base.py               # DocumentLoader interface
│   │   ├── discovery.py          # recursive search for *.md
│   │   ├── factory.py            # loader per file extension
│   │   ├── markdown_loader.py
│   │   ├── models.py             # Document
│   │   └── loader_service.py     # DocumentLoaderService
│   ├── embeddings/               # turning text into vectors
│   │   ├── base.py               # EmbeddingProvider interface
│   │   ├── factory.py
│   │   ├── gemini_embedding.py   # Gemini implementation
│   │   ├── models.py             # Embedding
│   │   └── service.py            # EmbeddingService
│   ├── indexer/
│   │   └── service.py            # DocumentIndexer: the whole indexing pipeline
│   ├── memory/                   # conversation history
│   │   ├── base.py               # MemoryProvider interface
│   │   ├── factory.py
│   │   ├── in_memory.py
│   │   └── models.py             # Message
│   ├── models/
│   │   └── chat_message.py       # ChatMessage, provider-independent roles
│   ├── prompts/
│   │   └── teacher.md            # system prompt
│   ├── providers/                # LLM providers
│   │   ├── base.py               # BaseProvider interface
│   │   ├── registry.py           # ProviderRegistry: name -> class
│   │   ├── factory.py            # ProviderFactory, builds the configured one
│   │   ├── gemini.py             # implemented
│   │   ├── openai.py             # registered, generate() not implemented
│   │   ├── claude.py             # registered, generate() not implemented
│   │   ├── groq.py               # registered, generate() not implemented
│   │   ├── ollama.py             # registered, generate() not implemented
│   │   ├── openrouter.py         # registered, generate() not implemented
│   │   └── azure_openai.py       # registered, generate() not implemented
│   ├── rag/                      # retrieval
│   │   ├── base.py               # Retriever interface
│   │   ├── context_builder.py    # renders documents into a context block
│   │   ├── empty.py              # retriever that finds nothing
│   │   ├── factory.py
│   │   ├── models.py             # Document
│   │   └── qdrant_retriever.py   # semantic search implementation
│   ├── scripts/                  # command line entry points
│   │   ├── index_docs.py         # indexing
│   │   ├── list_models.py        # available Gemini models
│   │   └── test_*.py             # manual checks of each layer
│   ├── services/
│   │   └── prompt_builder.py     # PromptBuilder
│   ├── vectorstore/              # vector database
│   │   ├── base.py               # VectorStore interface
│   │   ├── factory.py
│   │   ├── models.py             # SearchResult
│   │   ├── qdrant_store.py       # Qdrant implementation
│   │   └── service.py            # VectorStoreService
│   └── main.py                   # FastAPI application
├── bot/
│   ├── main.py                   # bot entry point
│   └── telegram_bot.py           # handlers, calls the REST API
├── docs/
│   └── demo/                     # demo documentation for indexing
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── LICENSE
└── .env.example
```

## Requirements

- Python 3.13 (only for running the scripts on the host; the containers bring
  their own interpreter)
- Docker 24 or newer
- Docker Compose v2
- A Gemini API key — https://aistudio.google.com/apikey

## Installation

```bash
git clone https://github.com/iamrlufe/devops-mentor-ai.git
cd devops-mentor-ai
```

Create the `.env` file from the template and fill in the secrets:

```bash
cp .env.example .env
```

At a minimum set `GEMINI_API_KEY`. `TELEGRAM_TOKEN` is only needed for the bot.

Start the stack:

```bash
docker compose up -d --build
```

Check that the API is alive:

```bash
curl http://localhost:8000/health
```

The interactive API documentation is at http://localhost:8000/docs.

## Configuration

All settings are read from `.env`. Empty values are read as empty strings, not
as "use the default", so keep the non-secret values from the template unless you
mean to change them.

| Variable | Description | Default |
| --- | --- | --- |
| `LLM_PROVIDER` | Which provider to build. See [Supported Providers](#supported-providers) | `gemini` |
| `GEMINI_API_KEY` | Gemini API key. Required for the implemented provider | — |
| `GEMINI_MODEL` | Model used for answers | `gemini-2.5-flash` |
| `GEMINI_EMBEDDING_MODEL` | Model used for embeddings | `gemini-embedding-001` |
| `QDRANT_URL` | Qdrant address | `http://localhost:6333` |
| `TELEGRAM_TOKEN` | Bot token from BotFather. Needed only for the bot | — |
| `API_URL` | Chat endpoint the bot calls | `http://api:8000/chat` |
| `POSTGRES_DB` | Database name, read by docker-compose | `devops_mentor` |
| `POSTGRES_USER` | Database user, read by docker-compose | `mentor` |
| `POSTGRES_PASSWORD` | Database password, read by docker-compose | — |

`QDRANT_URL` in `.env` is the value for running scripts on the host. The compose
file overrides it for the `api` container with `http://qdrant:6333`, because
inside a container `localhost` is the container itself.

PostgreSQL is started by the compose file, but the application does not connect
to it yet — it is reserved for persistent memory (see the roadmap).

### Provider settings

Only the settings of the selected provider are needed. Everything except Gemini
is optional, so an unused integration never blocks the start.

| Provider | Variables | Model default |
| --- | --- | --- |
| Gemini | `GEMINI_API_KEY`, `GEMINI_MODEL` | `gemini-2.5-flash` |
| OpenAI | `OPENAI_API_KEY`, `OPENAI_MODEL` | `gpt-4o-mini` |
| Claude | `CLAUDE_API_KEY`, `CLAUDE_MODEL` | `claude-sonnet-5` |
| Groq | `GROQ_API_KEY`, `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| Ollama | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | `llama3.1` |
| OpenRouter | `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` | `openai/gpt-4o-mini` |
| Azure OpenAI | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION` | deployment based |

`GEMINI_EMBEDDING_MODEL` is used for indexing and search no matter which chat
provider is selected, because Gemini is the only embedding implementation today.

## Supported Providers

**Implemented**

- ✅ Gemini

**Architecture ready**

- OpenAI
- Claude
- Groq
- Ollama
- OpenRouter
- Azure OpenAI

The providers marked *architecture ready* are registered and selectable: the
configuration is wired and the class exists, but `generate()` raises
`NotImplementedError` until the API call is written.

### Provider architecture

```
Teacher Agent
     │  knows only the factory
ProviderFactory        reads LLM_PROVIDER
     │  knows only the registry
ProviderRegistry       name -> provider class
     │
     ├── "gemini"        GeminiProvider        ✅ implemented
     ├── "openai"        OpenAIProvider
     ├── "claude"        ClaudeProvider
     ├── "groq"          GroqProvider
     ├── "ollama"        OllamaProvider
     ├── "openrouter"    OpenRouterProvider
     └── "azure_openai"  AzureOpenAIProvider
```

Each provider registers itself with a decorator, and the registry discovers the
classes by importing the modules of the package:

```python
@ProviderRegistry.register("gemini")
class GeminiProvider(BaseProvider):
    def generate(self, messages: list[ChatMessage]) -> str:
        ...
```

Adding a provider therefore takes two steps and touches no existing code:

1. Create `app/providers/<name>.py` with a class that implements
   `BaseProvider.generate(messages) -> str`.
2. Decorate it with `@ProviderRegistry.register("<name>")`.

There is no import list to extend and no `if/elif` in the factory. The agent,
the prompt builder and the memory work with a provider-independent
`ChatMessage` list, and each provider translates it into its own wire format —
Gemini, for instance, merges the system messages into a system instruction.

The same pattern is used for the other replaceable parts: `EmbeddingProvider`,
`VectorStore`, `Retriever`, `MemoryProvider` and `Chunker` each sit behind an
interface with a factory.

## Document Indexing

Put your markdown files into `docs/`. Subdirectories are searched recursively,
so any layout works:

```
docs/
├── demo/
│   ├── Docker.md
│   ├── Git.md
│   └── PowerShell.md
└── kubernetes/
    └── deployments.md
```

The first markdown heading becomes the document title; if the file has no
heading, the file name is used. Empty files are skipped.

Run the indexing:

```bash
docker compose exec api python -m app.scripts.index_docs docs
```

To index while running on the host (`QDRANT_URL` must point at
`http://localhost:6333`):

```bash
python -m app.scripts.index_docs docs
```

The output shows the pipeline and the result:

```
Loading...
Chunking...
Embedding...
Uploading...
Done.

Documents: 3
Chunks: 3
Embeddings: 3
Indexed: 3
```

The collection is recreated on every run, so the index never mixes new documents
with the previous ones. Re-run the command after changing the documentation.

## Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram and send `/newbot`.
2. Choose a display name and a username ending with `bot`.
3. BotFather replies with a token that looks like
   `123456789:AAErs-Gk1a2B3c4D5e6F7g8H9i0JkLmNoPq`.
4. Put it into `.env`:

   ```
   TELEGRAM_TOKEN=123456789:AAErs-Gk1a2B3c4D5e6F7g8H9i0JkLmNoPq
   ```

5. Restart the bot:

   ```bash
   docker compose up -d --build telegram-bot
   ```

Write to the bot in Telegram — it forwards the message to `API_URL` and replies
with the answer. Keep the token out of version control; `.env` is gitignored.

## REST API

### `GET /health`

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok"}
```

### `POST /chat`

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I build a Docker image?"}'
```

```json
{"answer": "To build an image you need a Dockerfile ..."}
```

The request body has a single field, `message`. The answer is generated with the
indexed documentation as context and is saved to the conversation history.

## Roadmap

### v1.0 — current

- REST API and Telegram bot
- RAG over markdown documentation: loading, chunking, embeddings, Qdrant
- Conversation memory in the process
- Extensible provider architecture: registry, factory and seven registered
  providers, Gemini implemented
- Docker deployment with pinned image versions

### v1.1

- Persistent memory in PostgreSQL and a real `chat_id` in the API, so the
  history survives a restart and separates users
- More providers: OpenAI, Claude, Ollama
- Reindexing only the documents that changed, instead of everything
- Structured logging and an index status endpoint

### v2.0

- Additional document formats: PDF, HTML, source code
- Hybrid search (semantic plus keyword) and reranking
- Streaming answers
- Web interface
- Tool calling: the assistant runs commands and reads their output

## License

Released under the MIT License — see [LICENSE](LICENSE).
