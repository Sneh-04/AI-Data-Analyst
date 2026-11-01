package com.aidataanalyst.repository;

import com.aidataanalyst.entity.Report;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ReportRepository extends JpaRepository<Report, Long> {
    List<Report> findAllByDatasetId(Long datasetId);
}
