package com.aidataanalyst.repository;

import com.aidataanalyst.entity.Dataset;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DatasetRepository extends JpaRepository<Dataset, Long> {
    Optional<Dataset> findByIdAndUploadedBy(Long id, Long uploadedBy);
}
