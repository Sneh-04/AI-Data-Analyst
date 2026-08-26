package com.aidataanalyst.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.Map;

@Entity
@Table(name = "dataset_versions")
public class DatasetVersion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "dataset_id", nullable = false)
    private Long datasetId;

    @Column(name = "version_number", nullable = false)
    private Integer versionNumber;

    @Column(name = "storage_path", nullable = false, length = 1000)
    private String storagePath;

    @Column(nullable = false, length = 100)
    private String operation;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "operation_params", columnDefinition = "jsonb")
    private Map<String, Object> operationParams;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "diff_summary", columnDefinition = "jsonb")
    private Map<String, Object> diffSummary;

    @Column(name = "created_by", nullable = false)
    private Long createdBy;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected DatasetVersion() {
    }

    public DatasetVersion(Long datasetId, Integer versionNumber, String storagePath, String operation,
                          Map<String, Object> operationParams, Map<String, Object> diffSummary, Long createdBy) {
        this.datasetId = datasetId;
        this.versionNumber = versionNumber;
        this.storagePath = storagePath;
        this.operation = operation;
        this.operationParams = operationParams;
        this.diffSummary = diffSummary;
        this.createdBy = createdBy;
        this.createdAt = Instant.now();
    }

    public Integer getVersionNumber() {
        return versionNumber;
    }

    public String getStoragePath() {
        return storagePath;
    }

    public String getOperation() {
        return operation;
    }

    public Map<String, Object> getOperationParams() {
        return operationParams;
    }

    public Map<String, Object> getDiffSummary() {
        return diffSummary;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
