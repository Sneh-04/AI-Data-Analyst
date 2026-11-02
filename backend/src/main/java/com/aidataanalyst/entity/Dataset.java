package com.aidataanalyst.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import org.hibernate.annotations.DynamicInsert;
import org.hibernate.annotations.DynamicUpdate;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.Map;

@Entity
@Table(name = "datasets")
@DynamicInsert
@DynamicUpdate
public class Dataset {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "workspace_id", nullable = false)
    private Long workspaceId;

    @Column(name = "uploaded_by", nullable = false)
    private Long uploadedBy;

    @Column(name = "file_name", nullable = false, length = 500)
    private String fileName;

    @Column(name = "storage_path", nullable = false, length = 1000)
    private String storagePath;

    @Column(name = "deletion_status", nullable = false, length = 16)
    private String deletionStatus = "ACTIVE";

    @Column(name = "row_count")
    private Integer rowCount;

    @Column(name = "column_count")
    private Integer columnCount;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "schema_json", columnDefinition = "jsonb")
    private Map<String, Object> schemaJson;

    @Column(name = "health_score")
    private Integer healthScore;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected Dataset() {
    }

    public Dataset(Long workspaceId, Long uploadedBy, String fileName, String storagePath,
                   Integer rowCount, Integer columnCount) {
        this.workspaceId = workspaceId;
        this.uploadedBy = uploadedBy;
        this.fileName = fileName;
        this.storagePath = storagePath;
        this.rowCount = rowCount;
        this.columnCount = columnCount;
        this.createdAt = Instant.now();
    }

    public Long getId() {
        return id;
    }

    public String getFileName() {
        return fileName;
    }

    public String getStoragePath() {
        return storagePath;
    }

    public String getDeletionStatus() {
        return deletionStatus;
    }

    public Long getUploadedBy() {
        return uploadedBy;
    }

    public void markDeletionPending() {
        this.deletionStatus = "DELETING";
    }

    public Integer getRowCount() {
        return rowCount;
    }

    public Integer getColumnCount() {
        return columnCount;
    }

    public Integer getHealthScore() {
        return healthScore;
    }

    public void setHealthScore(Integer healthScore) {
        this.healthScore = healthScore;
    }
}
