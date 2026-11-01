ALTER TABLE datasets
    ADD COLUMN deletion_status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    ADD CONSTRAINT chk_datasets_deletion_status
        CHECK (deletion_status IN ('ACTIVE', 'DELETING'));

CREATE TABLE dataset_deletion_jobs (
    id BIGSERIAL PRIMARY KEY,
    dataset_id BIGINT NOT NULL UNIQUE,
    requested_by_id BIGINT NOT NULL,
    status VARCHAR(16) NOT NULL CHECK (status IN ('IN_PROGRESS', 'FAILED', 'COMPLETED')),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);
