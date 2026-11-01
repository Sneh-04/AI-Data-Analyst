package com.aidataanalyst.repository;

import com.aidataanalyst.entity.DatasetDeletionJob;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface DatasetDeletionJobRepository extends JpaRepository<DatasetDeletionJob, Long> {
    Optional<DatasetDeletionJob> findByDatasetId(Long datasetId);
}
