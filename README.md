# DevOps Mentor AI Platform

An AI Agent Platform for learning, DevOps and system administration.

The platform is a set of replaceable layers rather than a wrapper around one
vendor. Agents, LLM providers, embeddings, conversation memory and retrievers
each sit behind an interface and are resolved through a registry, so adding one
means writing a new file — no existing module changes. That is the Open/Closed
Principle applied to every axis the project grows along.

Thirteen agents are registered today. Each answers with its own system prompt,
its own conversation history and retrieval-augmented generation over your
markdown documentation.

## Features

- **Multi-Agent Platform** — 13 registered agents, selected per request.
- **Five registries** — agents, providers, embeddings, memory, retrievers; all
  built on one generic `Registry`.
- **REST API** — FastAPI with `/chat`, `/agents`, `/health` and OpenAPI docs.
- **Telegram Bot** — long-polling bot on top of the same API.
- **RAG** — retrieved documentation is injected as a separate system message.
- **Vector Search** — semantic search over Qdrant with cosine distance.
- **Conversation Memory** — per agent and per chat, behind `MemoryProvider`.
- **Prompt System** — one markdown prompt per agent in `app/prompts/`.
- **Document Indexing** — one command turns markdown into a searchable index.
- **Capabilities** — agents and providers describe what they can do, ready for
  a coordinator that routes a question to the right agent.
- **Docker Deployment** — the whole stack starts with one compose command.

## Architecture

```
User
  │
Telegram Bot / REST API          POST /chat {"agent": "docker", "message": "..."}
  │
AgentFactory ──► AgentRegistry   name -> agent class
  │
Agent (Teacher, Docker, SQL, ...)
  │
  ├─► MemoryFactory   ──► MemoryRegistry     conversation history
  ├─► RetrieverFactory──► RetrieverRegistry  relevant documents
  │        │
  │   EmbeddingFactory ──► EmbeddingRegistry  query vector
  │        │
  │      Qdrant                               vector search
  ├─► ContextBuilder                          documents -> context block
  ├─► PromptBuilder                           system + context + history + question
  │
  └─► ProviderFactory ──► ProviderRegistry
           │
      Gemini / Groq / OpenAI / Claude / Ollama / OpenRouter / Azure OpenAI
```

### How a request is processed

1. `POST /chat` carries a `message` and an optional `agent`; without it the
   request goes to the teacher, exactly as before.
2. `AgentFactory` asks `AgentRegistry` for the class and returns a cached
   instance, so the provider and the clients are built once.
3. The agent loads the history of `agent:chat_id` — two agents in the same chat
   never read each other's conversation.
4. The retriever embeds the question and searches Qdrant for the 5 closest
   chunks; `ContextBuilder` renders them into a context block.
5. `PromptBuilder` assembles the messages: system prompt → retrieved context →
   history → question.
6. The provider translates that list into its own wire format and answers; the
   exchange is saved to memory.

If the index is missing or the search fails, the agent logs a warning and
answers without context instead of failing the request.

The indexing pipeline is separate and runs on demand:

```
docs/*.md → DocumentLoader → Chunker → Embeddings → Qdrant
```

## Multi-Agent Architecture

Every agent implements `BaseAgent`. The shared pipeline lives once in
`ConversationalAgent`, so an agent is a subclass with a few class attributes:

```python
@AgentRegistry.register("docker")
class DockerAgent(ConversationalAgent):
    name: ClassVar[str] = "docker"
    description: ClassVar[str] = "Docker images, containers and compose"
    capabilities: ClassVar[tuple[str, ...]] = ("docker", "containers")
    prompt_file: ClassVar[str] = "docker.md"
```

Adding an agent takes two files and touches no existing code:

1. `app/agents/<name>.py` with the decorated class.
2. `app/prompts/<name>.md` with its system prompt.

A missing prompt file is refused at construction with a message naming the file
and the agent, so a half-configured agent never reaches a user.

| Agent | Capabilities |
| --- | --- |
| `teacher` | learning, devops, mentoring |
| `infrastructure` | infrastructure, devops |
| `powershell` | powershell, windows, scripting |
| `linux` | linux, shell, administration |
| `docker` | docker, containers |
| `kubernetes` | kubernetes, orchestration |
| `terraform` | terraform, iac |
| `ansible` | ansible, configuration_management |
| `sql` | database, sql |
| `security` | security, hardening |
| `codereview` | review, code_quality |
| `documentation` | documentation, writing |
| `architecture` | design, architecture |

`GET /agents` returns the same list at runtime.

## Registries

All five registries are subclasses of one generic `Registry` in
`app/core/registry.py`; they differ only in the package they scan and the label
they use in error messages. There is exactly one implementation of the
registration, lookup and discovery logic in the project.

```python
class ProviderRegistry(Registry[BaseProvider], package="app.providers",
                       label="provider"):
    ...
```

Selecting an unregistered name raises a `ValueError` that lists what is
registered, and registering two different classes under one name is refused at
import time.

### Agent Registry

Package `app.agents`, selected per request or by `DEFAULT_AGENT`.
13 agents, all implemented.

### Provider Registry

Package `app.providers`, selected by `LLM_PROVIDER`.

| Provider | State | Capabilities |
| --- | --- | --- |
| `gemini` | ✅ implemented | chat, vision, files, json, reasoning |
| `groq` | ✅ implemented | chat, reasoning, tool_calling |
| `openai` | registered | chat, vision, audio, image, embedding |
| `claude` | registered | chat, reasoning, files |
| `ollama` | registered | chat, local, embedding |
| `openrouter` | registered | chat, reasoning, tool_calling |
| `azure_openai` | registered | chat, vision, embedding |

Groq uses the official OpenAI-compatible endpoint over `httpx`, so it needs no
extra dependency.

### Embedding Registry

Package `app.embeddings`, selected by `EMBEDDING_PROVIDER`.

| Provider | State |
| --- | --- |
| `gemini` | ✅ implemented, 3072 dimensions |
| `openai`, `voyageai`, `ollama`, `jina` | registered |

### Memory Registry

Package `app.memory`, selected by `MEMORY_PROVIDER`.

| Provider | State |
| --- | --- |
| `in_memory` | ✅ implemented, lost on restart |
| `redis`, `sqlite`, `postgres`, `mongo` | registered |

### Retriever Registry

Package `app.rag`, selected by `RETRIEVER_PROVIDER`.

| Retriever | State |
| --- | --- |
| `qdrant` | ✅ implemented |
| `empty` | ✅ implemented, finds nothing — run without an index |
| `chroma`, `milvus`, `pgvector`, `weaviate`, `pinecone` | registered |

A *registered* implementation is selectable and wired to its configuration, but
its methods raise `NotImplementedError` with a message naming what to implement.

## Project Structure

```
devops-mentor-ai/
├── app/
│   ├── core/
│   │   └── registry.py           # the generic Registry every layer reuses
│   ├── agents/
│   │   ├── base.py               # BaseAgent interface
│   │   ├── conversational.py     # the shared pipeline of every agent
│   │   ├── registry.py           # AgentRegistry
│   │   ├── factory.py            # AgentFactory
│   │   ├── teacher.py            # 13 agents, one file each
│   │   └── ...
│   ├── prompts/                  # one markdown system prompt per agent
│   ├── providers/                # LLM providers, 7 registered
│   │   ├── base.py               # BaseProvider + capabilities
│   │   ├── registry.py
│   │   ├── factory.py
│   │   ├── gemini.py             # implemented
│   │   ├── groq.py               # implemented
│   │   └── ...
│   ├── embeddings/               # text -> vectors, 5 registered
│   ├── memory/                   # conversation history, 5 registered
│   ├── rag/                      # retrieval, 7 registered
│   ├── vectorstore/              # Qdrant client behind VectorStore
│   ├── documents/                # reading markdown from disk
│   ├── chunking/                 # 1000 characters, 200 overlap
│   ├── indexer/                  # the whole indexing pipeline
│   ├── models/                   # ChatMessage, provider-independent roles
│   ├── services/                 # PromptBuilder
│   ├── config/                   # pydantic-settings
│   ├── scripts/                  # index_docs and manual checks per layer
│   └── main.py                   # FastAPI application
├── bot/                          # Telegram bot
├── docs/demo/                    # demo documentation for indexing
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── LICENSE
└── .env.example
```

## Requirements

- Python 3.13 (only for running the scripts on the host)
- Docker 24 or newer, Docker Compose v2
- A Gemini API key — https://aistudio.google.com/apikey

## Installation

```bash
git clone https://github.com/iamrlufe/devops-mentor-ai.git
cd devops-mentor-ai
```

```bash
cp .env.example .env
```

Set `GEMINI_API_KEY` at a minimum. `TELEGRAM_TOKEN` is only needed for the bot.

```bash
docker compose up -d --build
```

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
| `LLM_PROVIDER` | Chat provider | `gemini` |
| `EMBEDDING_PROVIDER` | Embedding provider | `gemini` |
| `MEMORY_PROVIDER` | Conversation memory | `in_memory` |
| `RETRIEVER_PROVIDER` | Retriever | `qdrant` |
| `DEFAULT_AGENT` | Agent used when the request names none | `teacher` |
| `GEMINI_API_KEY` | Gemini API key. Required | — |
| `GEMINI_MODEL` | Model used for answers | `gemini-2.5-flash` |
| `GEMINI_EMBEDDING_MODEL` | Model used for embeddings | `gemini-embedding-001` |
| `GROQ_API_KEY` | Groq API key | — |
| `GROQ_MODEL` | Groq model | `llama-3.3-70b-versatile` |
| `GROQ_BASE_URL` | OpenAI-compatible endpoint | `https://api.groq.com/openai/v1` |
| `QDRANT_URL` | Qdrant address | `http://localhost:6333` |
| `TELEGRAM_TOKEN` | Bot token from BotFather | — |
| `API_URL` | Chat endpoint the bot calls | `http://api:8000/chat` |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Read by docker-compose | — |

The keys of the registered but unimplemented integrations (`OPENAI_API_KEY`,
`CLAUDE_API_KEY`, `OPENROUTER_API_KEY`, `AZURE_OPENAI_*`, `VOYAGEAI_API_KEY`,
`JINA_API_KEY`, `OLLAMA_BASE_URL`) are listed in `.env.example` and may stay
empty.

`QDRANT_URL` in `.env` is the value for running scripts on the host. The compose
file overrides it for the `api` container with `http://qdrant:6333`.

PostgreSQL is started by the compose file, but the application does not connect
to it yet — it is reserved for the persistent memory provider.

## Document Indexing

Put your markdown files into `docs/`; subdirectories are searched recursively.
The first heading becomes the title, empty files are skipped.

```bash
docker compose exec api python -m app.scripts.index_docs docs
```

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
with the previous ones. All agents share the same index.

## REST API

### `GET /health`

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok"}
```

### `GET /agents`

```bash
curl http://localhost:8000/agents
```

```json
{
  "default": "teacher",
  "agents": [
    {"name": "ansible", "description": "Ansible playbooks and configuration management",
     "capabilities": ["ansible", "configuration_management"]}
  ]
}
```

### `POST /chat`

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"agent": "docker", "message": "How do I build an image?"}'
```

```json
{"answer": "To build an image you need a Dockerfile ...", "agent": "docker"}
```

`agent` is optional — without it the teacher answers, so clients written against
v1.0 keep working unchanged. An unknown agent returns `400` with the list of
registered names.

## Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) and send `/newbot`.
2. Choose a display name and a username ending with `bot`.
3. Put the token into `.env` as `TELEGRAM_TOKEN`.
4. Restart the bot:

   ```bash
   docker compose up -d --build telegram-bot
   ```

The bot forwards every message to `API_URL` without naming an agent, so it talks
to the teacher. Because the agent is chosen per request, adding `/agent docker`
later is a change in the bot only — the platform already accepts the field.

## Roadmap

### v1.1 — current

- Multi-agent platform: 13 agents, agent selection in the API
- Five registries on one generic implementation
- Groq provider implemented next to Gemini
- Capabilities on agents and providers

### v1.2

- `CoordinatorAgent` that routes a question by capabilities
- Persistent memory (PostgreSQL, Redis) and a real `chat_id` in the API
- More providers: OpenAI, Claude, Ollama
- Reindexing only the documents that changed

### v2.0

- More document formats: PDF, HTML, source code
- Hybrid search and reranking
- Streaming answers, web interface
- Tool calling: agents run commands and read the output

## License

Released under the MIT License — see [LICENSE](LICENSE).
