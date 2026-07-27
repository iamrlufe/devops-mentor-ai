-- Platform persistence: profiles, workspaces, conversations and memory.
-- Plain SQL, applied by app/scripts/migrate.py in file name order.

CREATE TABLE IF NOT EXISTS users (
    user_id            TEXT PRIMARY KEY,
    telegram_id        TEXT UNIQUE,
    name               TEXT        NOT NULL DEFAULT '',
    phone              TEXT        NOT NULL DEFAULT '',
    language           TEXT        NOT NULL DEFAULT 'ru',
    timezone           TEXT        NOT NULL DEFAULT 'UTC',
    preferred_agent    TEXT        NOT NULL DEFAULT '',
    preferred_provider TEXT        NOT NULL DEFAULT '',
    last_agent         TEXT        NOT NULL DEFAULT '',
    last_provider      TEXT        NOT NULL DEFAULT '',
    message_count      INTEGER     NOT NULL DEFAULT 0,
    conversation_count INTEGER     NOT NULL DEFAULT 0,
    registration_source TEXT       NOT NULL DEFAULT '',
    metadata           JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen          TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS workspaces (
    chat_id    TEXT PRIMARY KEY,
    user_id    TEXT        NOT NULL DEFAULT '',
    agent      TEXT        NOT NULL DEFAULT '',
    provider   TEXT        NOT NULL DEFAULT '',
    embedding  TEXT        NOT NULL DEFAULT '',
    memory     TEXT        NOT NULL DEFAULT '',
    retriever  TEXT        NOT NULL DEFAULT '',
    collection TEXT        NOT NULL DEFAULT '',
    prompt     TEXT        NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS workspaces_user_id_idx ON workspaces (user_id);

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    user_id         TEXT        NOT NULL DEFAULT '',
    chat_id         TEXT        NOT NULL DEFAULT '',
    agent           TEXT        NOT NULL DEFAULT '',
    provider        TEXT        NOT NULL DEFAULT '',
    title           TEXT        NOT NULL DEFAULT '',
    message_count   INTEGER     NOT NULL DEFAULT 0,
    metadata        JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS conversations_user_id_idx ON conversations (user_id);
CREATE INDEX IF NOT EXISTS conversations_chat_agent_idx
    ON conversations (chat_id, agent);

CREATE TABLE IF NOT EXISTS conversation_messages (
    message_id      BIGSERIAL PRIMARY KEY,
    conversation_id TEXT        NOT NULL
        REFERENCES conversations (conversation_id) ON DELETE CASCADE,
    user_id         TEXT        NOT NULL DEFAULT '',
    agent           TEXT        NOT NULL DEFAULT '',
    provider        TEXT        NOT NULL DEFAULT '',
    role            TEXT        NOT NULL,
    message         TEXT        NOT NULL,
    tokens          INTEGER     NOT NULL DEFAULT 0,
    metadata        JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS conversation_messages_conversation_idx
    ON conversation_messages (conversation_id, message_id);

-- Memory is the fast lookup the prompt builder reads; the conversation tables
-- above stay the source of truth.
CREATE TABLE IF NOT EXISTS memory_messages (
    message_id BIGSERIAL PRIMARY KEY,
    chat_key   TEXT        NOT NULL,
    role       TEXT        NOT NULL,
    content    TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS memory_messages_chat_key_idx
    ON memory_messages (chat_key, message_id);
