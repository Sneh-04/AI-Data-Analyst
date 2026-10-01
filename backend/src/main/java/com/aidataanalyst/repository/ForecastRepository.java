package com.aidataanalyst.repository;

import com.aidataanalyst.entity.Forecast;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ForecastRepository extends JpaRepository<Forecast, Long> {
    List<Forecast> findByDatasetIdOrderByCreatedAtDesc(Long datasetId);
}