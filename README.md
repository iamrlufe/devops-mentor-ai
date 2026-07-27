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
- **Prompt System** — a `PromptRegistry` resolves prompts by name from
  markdown files or from memory, so an agent never touches the filesystem.
- **Document Indexing** — one command turns markdown into a searchable index.
- **Capabilities** — agents and providers describe what they can do, ready for
  a coordinator that routes a question to the right agent.
- **User Profiles** — a profile is created on first contact, with a platform
  `user_id` that is independent of the messenger.
- **Telegram UX** — menu keyboard, inline agent and provider pickers and a
  first-run setup.
- **Runtime Workspaces** — every user picks their own agent, provider,
  embedding, memory, retriever and collection at runtime, without
  affecting anyone else.
- **Per-agent collections** — every agent may search its own vector
  collection, or share the platform one.
- **Versioned API** — `/api/v1/...`, with the original paths still served.
- **Health reporting** — `/health` reports the state of every component.
- **Docker Deployment** — the whole stack starts with one compose command.

## Architecture

```
User
  │
Telegram Bot / REST API          POST /chat {"chat_id": "123", "message": "..."}
  │
WorkspaceManager ──► AgentRegistry   workspace -> agent class
  │
RuntimeContextBuilder                names -> resolved stack
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

1. `POST /chat` carries a `message`, an optional `chat_id` and an optional
   `agent`; without them the request goes to the default workspace and the
   default agent, exactly as before workspaces existed.
2. `WorkspaceManager` reads the workspace of that chat and
   `RuntimeContextBuilder` resolves its names into a `RuntimeContext`; the
   agent is constructed with it and builds nothing itself.
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

## Workspace Architecture

A workspace is the stack one user works with. Switching an agent or a provider
changes that user's workspace only; everyone else keeps working on theirs.

```
User
  │
Workspace          agent, provider, embedding, memory, retriever, collection
  │
Agent              receives a RuntimeContext, builds nothing itself
  │
Provider           Gemini / Groq / ...
  │
Embedding          the query vector
  │
Retriever          searches the collection of the workspace
  │
Vector Store       Qdrant
```

Every field holds a **name**, never an object, and an empty name falls through
three levels: what the workspace sets, then what the agent declares, then the
platform settings. `RuntimeContextBuilder` resolves those names once per
request and hands the agent a `RuntimeContext` — the agent itself never touches
a factory, a registry or a setting.

### REST

Read a workspace, with what it resolves to:

```bash
curl "http://localhost:8000/api/v1/workspace?chat_id=123"
```

```json
{
  "workspace": {"chat_id": "123", "agent": "", "provider": "", "embedding": "",
                "memory": "", "retriever": "", "collection": "", "prompt": ""},
  "resolved": {"chat_id": "123", "agent": "teacher", "provider": "gemini",
               "embedding": "gemini", "memory": "in_memory",
               "retriever": "qdrant", "collection": "mentor_documents",
               "prompt": "teacher"}
}
```

Change the stack of one user:

```bash
curl -X POST http://localhost:8000/api/v1/workspace \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123", "agent": "docker", "provider": "groq"}'
```

```json
{"success": true, "workspace": {"chat_id": "123", "agent": "docker",
 "provider": "groq", "embedding": "", "memory": "", "retriever": "",
 "collection": "", "prompt": ""}}
```

Every later message of that chat runs on the Docker agent and Groq:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123", "message": "How do I build an image?"}'
```

```json
{"answer": "...", "agent": "docker", "provider": "groq", "chat_id": "123"}
```

Other endpoints: `GET /api/v1/workspaces` lists every workspace in use,
`GET /api/v1/workspace/{chat_id}` reads one, `GET /api/v1/providers` lists what
each provider supports.

Selecting a provider that is registered but not implemented is refused with a
message naming the ones that work, so a workspace never ends up unusable:

```json
{"detail": "Provider 'openai' is registered but not implemented yet. Implemented providers: gemini, groq."}
```

### Telegram

The bot uses the Telegram chat id as the workspace key, so every chat has its
own stack.

```
/agents              list the agents
/providers           list the providers and whether each one works yet
/agent docker        switch this chat to the Docker agent
/provider groq       switch this chat to Groq
/workspace           show what this chat runs on
```

`/workspace` answers with the resolved stack:

```
Agent:
docker

Provider:
groq

Embedding:
gemini

Retriever:
qdrant

Memory:
in_memory

Collection:
mentor_documents
```

## User Profiles

A profile is created automatically on the first message. There is no
registration, no login and no password: the messenger id is only an external
key.

```
Telegram id 100001  ──►  usr_c4c0f0c8106d  ──►  workspace + memory
```

The platform id (`usr_…`) is generated by the platform and never derived from
the Telegram id, so the same profile can later be reached from REST, Discord,
Slack or a web interface. Everything below the profile — workspace, history,
collection — is keyed by `user_id`.

A profile holds `user_id`, `telegram_id`, `name`, optional `phone`, `language`,
`timezone`, `created_at`, `updated_at`, `preferred_agent`, `preferred_provider`
and free-form `metadata`. Profiles live behind `UserStore`, selected by
`USER_STORE`, so a persistent store is a new class in `app/users/` and nothing
else.

**Profile and workspace are different things.** The profile says who the user
is; the workspace says what they run on. The workspace carries the `user_id` of
its owner.

### First run

```
Здравствуйте!
Добро пожаловать в DevOps Mentor AI.
Как мне к Вам обращаться?
        → Роман
Приятно познакомиться, Роман!
Хотите указать номер телефона? Это необязательно — можно пропустить.
        [📱 Отправить номер] [Пропустить]
Настройка завершена.
Имя: Роман
User ID: usr_c4c0f0c8106d
Agent: teacher
Provider: groq
Workspace: usr_c4c0f0c8106d
```

## Telegram UX

The bot opens with a persistent menu:

```
💬 Чат        👤 Профиль
🤖 Агенты     🧠 Провайдеры
⚙ Workspace   📚 Помощь
ℹ О проекте
```

Agents and providers are chosen with inline buttons. The provider list marks
what is not finished yet and refuses to select it:

```
🔒 azure_openai — Coming Soon    🔒 claude — Coming Soon
gemini                           ✅ groq
🔒 ollama — Coming Soon          🔒 openai — Coming Soon
🔒 openrouter — Coming Soon
```

Picking one updates that user's workspace immediately; every later message uses
it. Commands keep working alongside the buttons.

### Bot commands

| Command | What it does |
| --- | --- |
| `/start` | Greeting and first-run setup |
| `/help` | How the platform works, how to switch things |
| `/about` | What the project is, architecture, GitHub, licence |
| `/version` | Version, release date, git tag |
| `/profile` | Name, user id, telegram id, agent, provider, workspace, language, timezone, phone, registration date |
| `/editprofile` | Ask the name and phone again |
| `/whoami` | Short identity |
| `/status` | Platform version, LLM, embedding, retriever, memory, RAG, collection, document count |
| `/reset` | Put the workspace back to platform defaults |
| `/agents` | Agent picker |
| `/providers` | Provider picker |
| `/workspace` | What this user runs on |
| `/agent <name>` | Switch the agent from the command line |
| `/provider <name>` | Switch the provider from the command line |

### Runtime switching

Everything is per user and takes effect on the next message:

```
/agent docker      → this user now talks to the Docker agent
/provider gemini   → this user now runs on Gemini
/workspace         → shows the resolved stack
/reset             → back to the platform defaults
```

Two Telegram users in the same bot keep separate profiles, workspaces and
conversation histories.

## Multi-Agent Architecture

Every agent implements `BaseAgent`. The shared pipeline lives once in
`ConversationalAgent`, so an agent is a subclass with a few class attributes:

```python
@AgentRegistry.register("docker")
class DockerAgent(ConversationalAgent):
    name: ClassVar[str] = "docker"
    description: ClassVar[str] = "Docker images, containers and compose"
    version: ClassVar[str] = "1.0.0"
    author: ClassVar[str] = "DevOps Mentor AI Platform"
    tags: ClassVar[tuple[str, ...]] = ("containers", "build")
    capabilities: ClassVar[tuple[str, ...]] = ("docker", "containers")
    prompt: ClassVar[str] = "docker"
```

An agent is described, not programmed. Besides its identity it may declare the
stack it runs on, and an empty value means "follow the platform settings":

```python
    default_provider: ClassVar[str] = "groq"          # this agent uses Groq
    default_embedding: ClassVar[str] = ""             # platform default
    default_memory: ClassVar[str] = ""                # platform default
    default_retriever: ClassVar[str] = ""             # platform default
    collection: ClassVar[str] = "docker_documents"    # its own documents
```

Nothing in the agent pipeline changes when these values change: the prompt is
resolved through the `PromptRegistry` and the rest through the factories.

Adding an agent takes two files and touches no existing code:

1. `app/agents/<name>.py` with the decorated class.
2. `app/prompts/<name>.md` with its system prompt — or a
   `PromptRegistry.register("<name>", "...")` call, since prompts do not have
   to come from disk.

A missing prompt is refused at construction with a message naming the prompt and
where to put it, so a half-configured agent never reaches a user.

`GET /agents` returns the full metadata of every agent: version, author, tags,
capabilities and the stack it declares.

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

Currently implemented providers

- Gemini
- Groq

Architecture supports

- OpenAI
- Claude
- Ollama
- OpenRouter
- Azure OpenAI

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
| `openai`, `voyageai`, `ollama`, `azure_openai`, `jina` | registered |

### Memory Registry

Package `app.memory`, selected by `MEMORY_PROVIDER`.

| Provider | State |
| --- | --- |
| `in_memory` | ✅ implemented, lost on restart, capped by `MEMORY_MAX_MESSAGES` |
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

### Collections

Every agent may search its own collection. An agent that declares nothing uses
the shared collection from `QDRANT_COLLECTION`, which is what all shipped agents
do, so one index serves the whole platform out of the box.

```python
class DockerAgent(ConversationalAgent):
    collection: ClassVar[str] = "docker_documents"
```

Index that collection by naming it:

```bash
docker compose exec api python -m app.scripts.index_docs docs/docker docker_documents
```

The retriever, the vector store factory and the indexer all take the collection
as an argument, so a per-agent index needs no code change — only the attribute
and a run of the indexer.

## Project Structure

```
devops-mentor-ai/
├── app/
│   ├── core/
│   │   └── registry.py           # the generic Registry every layer reuses
│   ├── api/
│   │   ├── routes.py             # handlers, mounted at /api/v1 and at /
│   │   └── health.py             # component probes for /health
│   ├── prompting/
│   │   └── registry.py           # PromptRegistry: name -> prompt text
│   ├── users/                    # user profiles behind a registry
│   │   ├── models.py             # UserProfile, usr_ identifiers
│   │   ├── base.py               # UserStore interface
│   │   ├── registry.py
│   │   ├── factory.py
│   │   ├── in_memory.py
│   │   └── manager.py            # UserManager
│   ├── agents/
│   │   ├── base.py               # BaseAgent interface
│   │   ├── conversational.py     # the shared pipeline of every agent
│   │   ├── registry.py           # AgentRegistry
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
│   ├── keyboards.py              # menu and inline pickers
│   └── texts.py                  # user facing text
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
| `MEMORY_MAX_MESSAGES` | Messages kept per chat by the in-process memory, `0` disables the cap | `100` |
| `WORKSPACE_STORE` | Where runtime workspaces are kept | `in_memory` |
| `USER_STORE` | Where user profiles are kept | `in_memory` |
| `DEFAULT_LANGUAGE` | Language a new profile starts with | `ru` |
| `DEFAULT_TIMEZONE` | Timezone a new profile starts with | `UTC` |
| `DEFAULT_CHAT_ID` | Conversation used when a request names no chat | `default` |
| `GEMINI_API_KEY` | Gemini API key. Required | — |
| `GEMINI_MODEL` | Model used for answers | `gemini-2.5-flash` |
| `GEMINI_EMBEDDING_MODEL` | Model used for embeddings | `gemini-embedding-001` |
| `GROQ_API_KEY` | Groq API key | — |
| `GROQ_MODEL` | Groq model | `llama-3.3-70b-versatile` |
| `GROQ_BASE_URL` | OpenAI-compatible endpoint | `https://api.groq.com/openai/v1` |
| `QDRANT_URL` | Qdrant address | `http://localhost:6333` |
| `QDRANT_COLLECTION` | Collection shared by agents that declare none | `mentor_documents` |
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

The second argument selects a collection, which is how an agent with its own
collection is indexed:

```bash
docker compose exec api python -m app.scripts.index_docs docs docker_documents
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
with the previous ones.

## REST API

Every endpoint is served twice: under `/api/v1` as the documented API, and on
the original path for clients written before versioning. The two mounts share
one implementation, so they can never drift apart.

```
/api/v1/health   ==   /health
/api/v1/agents   ==   /agents
/api/v1/chat     ==   /chat
```

### `GET /api/v1/health`

```bash
curl http://localhost:8000/api/v1/health
```

```json
{
  "status": "ok",
  "name": "DevOps Mentor AI Platform",
  "version": "1.0.0",
  "llm_provider": "gemini",
  "embedding_provider": "gemini",
  "memory_provider": "in_memory",
  "retriever_provider": "qdrant",
  "vector_store": {"url": "http://qdrant:6333", "collection": "mentor_documents"},
  "components": [
    {"name": "llm:gemini", "status": "ok"},
    {"name": "embedding:gemini", "status": "ok"},
    {"name": "memory:in_memory", "status": "ok"},
    {"name": "retriever:qdrant", "status": "ok"},
    {"name": "vector_store:mentor_documents", "status": "ok"}
  ]
}
```

The top level `status` is `ok` while every component answers and `degraded` when
one of them fails, with the reason in that component's `detail`. A failing
component never turns the health check itself into an error.

### `GET /api/v1/agents`

```bash
curl http://localhost:8000/api/v1/agents
```

```json
{
  "default": "teacher",
  "agents": [
    {"name": "docker", "description": "Docker images, containers and compose",
     "version": "1.0.0", "author": "DevOps Mentor AI Platform",
     "tags": ["containers", "build"], "capabilities": ["docker", "containers"],
     "prompt": "docker", "provider": "", "embedding": "", "memory": "",
     "retriever": "", "collection": ""}
  ]
}
```

An empty `provider`, `embedding`, `memory`, `retriever` or `collection` means
the agent follows the platform settings.

### `POST /api/v1/chat`

```bash
curl -X POST http://localhost:8000/api/v1/chat \
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

### v1.0 — current

- Multi-agent platform: 13 agents, agent selection in the API
- Five registries on one generic implementation
- Gemini and Groq providers implemented
- Declarative agents: metadata plus the provider, memory, retriever, collection
  and prompt they run on
- Prompt registry, per-agent collections, versioned API, component health

### v1.1

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
