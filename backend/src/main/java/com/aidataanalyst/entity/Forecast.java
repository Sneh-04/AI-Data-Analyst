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
@Table(name = "forecasts")
public class Forecast {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "dataset_id", nullable = false)
    private Long datasetId;

    @Column(name = "date_column", nullable = false, length = 255)
    private String dateColumn;

    @Column(name = "value_column", nullable = false, length = 255)
    private String valueColumn;

    @Column(name = "model_used", nullable = false, length = 50)
    private String modelUsed;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "model_comparison", columnDefinition = "jsonb")
    private Map<String, Object> modelComparison;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "forecast_json", nullable = false, columnDefinition = "jsonb")
    private Object forecastJson;

    @Column(name = "created_by", nullable = false)
    private Long createdBy;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    protected Forecast() {
    }

    public Forecast(Long datasetId, String dateColumn, String valueColumn, String modelUsed,
                    Map<String, Object> modelComparison, Object forecastJson, Long createdBy) {
        this.datasetId = datasetId;
        this.dateColumn = dateColumn;
        this.valueColumn = valueColumn;
        this.modelUsed = modelUsed;
        this.modelComparison = modelComparison;
        this.forecastJson = forecastJson;
        this.createdBy = createdBy;
        this.createdAt = Instant.now();
    }

    public Long getId() {
        return id;
    }

    public Long getDatasetId() {
        return datasetId;
    }

    public String getDateColumn() {
        return dateColumn;
    }

    public String getValueColumn() {
        return valueColumn;
    }

    public String getModelUsed() {
        return modelUsed;
    }

    public Map<String, Object> getModelComparison() {
        return modelComparison;
    }

    public Object getForecastJson() {
        return forecastJson;
    }

    public Long getCreatedBy() {
        return createdBy;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}