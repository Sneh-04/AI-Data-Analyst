package com.aidataanalyst.repository;

import com.aidataanalyst.entity.Report;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReportRepository extends JpaRepository<Report, Long> {
}
