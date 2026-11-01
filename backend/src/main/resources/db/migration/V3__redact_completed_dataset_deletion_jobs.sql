ALTER TABLE dataset_deletion_jobs
    ALTER COLUMN dataset_id DROP NOT NULL,
    ALTER COLUMN requested_by_id DROP NOT NULL;

UPDATE dataset_deletion_jobs
SET dataset_id = NULL,
    requested_by_id = NULL
WHERE status = 'COMPLETED';
