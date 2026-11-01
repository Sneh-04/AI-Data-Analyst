package com.aidataanalyst.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.Instant;

@Entity
@Table(name = "dataset_deletion_jobs")
public class DatasetDeletionJob {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "dataset_id", unique = true)
    private Long datasetId;

    @Column(name = "requested_by_id")
    private Long requestedById;

    @Column(nullable = false, length = 16)
    private String status;

    @Column(name = "requested_at", nullable = false)
    private Instant requestedAt;

    @Column(name = "completed_at")
    private Instant completedAt;

    protected DatasetDeletionJob() {
    }

    public DatasetDeletionJob(Long datasetId, Long requestedById) {
        this.datasetId = datasetId;
        this.requestedById = requestedById;
        this.status = "IN_PROGRESS";
        this.requestedAt = Instant.now();
    }

    public Long getId() {
        return id;
    }

    public Long getDatasetId() {
        return datasetId;
    }

    public Long getRequestedById() {
        return requestedById;
    }

    public String getStatus() {
        return status;
    }

    public void markInProgress() {
        this.status = "IN_PROGRESS";
    }

    public void markFailed() {
        this.status = "FAILED";
    }

    public void markCompleted() {
        this.status = "COMPLETED";
        this.completedAt = Instant.now();
        this.datasetId = null;
        this.requestedById = null;
    }
}
