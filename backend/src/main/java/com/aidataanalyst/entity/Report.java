package com.aidataanalyst.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.Instant;

@Entity
@Table(name = "reports")
public class Report {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "dataset_id", nullable = false)
    private Long datasetId;

    @Column(nullable = false, length = 10)
    private String format;

    @Column(name = "storage_path", nullable = false, length = 1000)
    private String storagePath;

    @Column(name = "generated_by", nullable = false)
    private Long generatedBy;

    @Column(nullable = false)
    private boolean scheduled = false;

    @Column(name = "cron_expression", length = 100)
    private String cronExpression;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected Report() {
    }

    public Report(Long datasetId, String format, String storagePath, Long generatedBy) {
        this.datasetId = datasetId;
        this.format = format;
        this.storagePath = storagePath;
        this.generatedBy = generatedBy;
        this.createdAt = Instant.now();
    }
}
