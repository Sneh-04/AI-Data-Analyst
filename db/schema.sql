-- AI Data Analyst Platform - core schema
-- The original Streamlit repo has ZERO persistence (everything lives in
-- st.session_state and disappears on refresh). This schema is what makes
-- the platform multi-user, auditable, and resumable.

CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    role            VARCHAR(20) NOT NULL DEFAULT 'ANALYST', -- ADMIN | ANALYST | VIEWER
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE workspaces (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    owner_id        BIGINT NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE workspace_members (
    workspace_id    BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL DEFAULT 'ANALYST',
    PRIMARY KEY (workspace_id, user_id)
);

CREATE TABLE datasets (
    id              BIGSERIAL PRIMARY KEY,
    workspace_id    BIGINT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    uploaded_by     BIGINT NOT NULL REFERENCES users(id),
    file_name       VARCHAR(500) NOT NULL,
    storage_path    VARCHAR(1000) NOT NULL, -- S3 / local object storage key
    row_count       INTEGER,
    column_count    INTEGER,
    schema_json     JSONB,                  -- column name -> inferred dtype
    health_score    INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Every cleaning operation is versioned instead of silently overwriting data
CREATE TABLE dataset_versions (
    id              BIGSERIAL PRIMARY KEY,
    dataset_id      BIGINT NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    version_number  INTEGER NOT NULL,
    storage_path    VARCHAR(1000) NOT NULL,
    operation       VARCHAR(100) NOT NULL,  -- 'fill_missing' | 'remove_duplicates' | 'outlier_iqr' | ...
    operation_params JSONB,
    diff_summary    JSONB,                  -- rows_removed, nulls_fixed, etc from cleaning_service
    created_by      BIGINT NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (dataset_id, version_number)
);

CREATE TABLE dashboards (
    id              BIGSERIAL PRIMARY KEY,
    dataset_id      BIGINT NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    created_by      BIGINT NOT NULL REFERENCES users(id),
    title           VARCHAR(255) NOT NULL,
    layout_json      JSONB NOT NULL,        -- widget positions + chart configs
    is_shared       BOOLEAN NOT NULL DEFAULT false,
    share_token     VARCHAR(64) UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE forecasts (
    id              BIGSERIAL PRIMARY KEY,
    dataset_id      BIGINT NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    date_column     VARCHAR(255) NOT NULL,
    value_column    VARCHAR(255) NOT NULL,
    model_used      VARCHAR(50) NOT NULL,
    model_comparison JSONB,
    forecast_json   JSONB NOT NULL,
    created_by      BIGINT NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE reports (
    id              BIGSERIAL PRIMARY KEY,
    dataset_id      BIGINT NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    format          VARCHAR(10) NOT NULL,   -- PDF | XLSX | MD
    storage_path    VARCHAR(1000) NOT NULL,
    generated_by    BIGINT NOT NULL REFERENCES users(id),
    scheduled       BOOLEAN NOT NULL DEFAULT false,
    cron_expression VARCHAR(100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE chat_sessions (
    id              BIGSERIAL PRIMARY KEY,
    dataset_id      BIGINT NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    user_id         BIGINT NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE chat_messages (
    id              BIGSERIAL PRIMARY KEY,
    session_id      BIGINT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role            VARCHAR(10) NOT NULL,   -- 'user' | 'assistant'
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    user_id         BIGINT REFERENCES users(id),
    action          VARCHAR(100) NOT NULL,  -- 'DATASET_UPLOAD' | 'CLEANING_RUN' | 'FORECAST_RUN' | ...
    entity_type     VARCHAR(50),
    entity_id       BIGINT,
    metadata        JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_datasets_workspace ON datasets(workspace_id);
CREATE INDEX idx_versions_dataset ON dataset_versions(dataset_id);
CREATE INDEX idx_forecasts_dataset ON forecasts(dataset_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);

-- pgvector extension for Phase 3 RAG-based chat upgrade (embeddings over
-- dataset schema + row samples). Left commented until that phase starts.
CREATE EXTENSION IF NOT EXISTS vector;
ALTER TABLE datasets ADD COLUMN schema_embedding vector(1536);
