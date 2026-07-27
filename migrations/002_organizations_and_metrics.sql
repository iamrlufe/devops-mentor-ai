-- Every record belongs to an organization, and every request is measured.
-- One organization exists today; the columns are what makes more than one
-- possible later without touching the tables again.

CREATE TABLE IF NOT EXISTS organizations (
    organization_id TEXT PRIMARY KEY,
    name            TEXT        NOT NULL,
    slug            TEXT        NOT NULL DEFAULT '',
    plan            TEXT        NOT NULL DEFAULT 'default',
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    metadata        JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO organizations (organization_id, name, slug)
VALUES ('org_default', 'Default', 'default')
ON CONFLICT (organization_id) DO NOTHING;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org_default';
ALTER TABLE workspaces
    ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org_default';
ALTER TABLE conversations
    ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org_default';
ALTER TABLE conversation_messages
    ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org_default';

CREATE INDEX IF NOT EXISTS users_organization_idx ON users (organization_id);
CREATE INDEX IF NOT EXISTS workspaces_organization_idx
    ON workspaces (organization_id);
CREATE INDEX IF NOT EXISTS conversations_organization_idx
    ON conversations (organization_id);
CREATE INDEX IF NOT EXISTS conversation_messages_organization_idx
    ON conversation_messages (organization_id);

-- One row per answered or failed request. This is where the administration
-- reads latency, error counts and provider usage from.
CREATE TABLE IF NOT EXISTS request_metrics (
    request_id      BIGSERIAL PRIMARY KEY,
    organization_id TEXT        NOT NULL DEFAULT 'org_default',
    user_id         TEXT        NOT NULL DEFAULT '',
    chat_id         TEXT        NOT NULL DEFAULT '',
    agent           TEXT        NOT NULL DEFAULT '',
    provider        TEXT        NOT NULL DEFAULT '',
    embedding       TEXT        NOT NULL DEFAULT '',
    retriever       TEXT        NOT NULL DEFAULT '',
    memory          TEXT        NOT NULL DEFAULT '',
    latency_ms      INTEGER     NOT NULL DEFAULT 0,
    success         BOOLEAN     NOT NULL DEFAULT TRUE,
    error           TEXT        NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS request_metrics_created_idx
    ON request_metrics (created_at DESC);
CREATE INDEX IF NOT EXISTS request_metrics_provider_idx
    ON request_metrics (provider, created_at DESC);
CREATE INDEX IF NOT EXISTS request_metrics_agent_idx
    ON request_metrics (agent, created_at DESC);
CREATE INDEX IF NOT EXISTS request_metrics_organization_idx
    ON request_metrics (organization_id);
