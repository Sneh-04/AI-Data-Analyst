package com.aidataanalyst.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

import java.time.Instant;

@Entity
@Table(name = "dataset_health_scores")
public class DatasetHealthScore {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "dataset_id", nullable = false)
    private Dataset dataset;

    @Column(nullable = false)
    private Integer score;

    @Column(nullable = false, length = 32)
    private String grade;

    @Column(name = "assessed_at", nullable = false)
    private Instant assessedAt;

    protected DatasetHealthScore() {
    }

    public DatasetHealthScore(Dataset dataset, Integer score, String grade) {
        this.dataset = dataset;
        this.score = score;
        this.grade = grade;
        this.assessedAt = Instant.now();
    }

    public Long getId() {
        return id;
    }

    public Integer getScore() {
        return score;
    }

    public String getGrade() {
        return grade;
    }

    public Instant getAssessedAt() {
        return assessedAt;
    }
}
