package com.aidataanalyst.repository;

import com.aidataanalyst.entity.DatasetVersion;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface DatasetVersionRepository extends JpaRepository<DatasetVersion, Long> {
    List<DatasetVersion> findByDatasetIdOrderByVersionNumberDesc(Long datasetId);
    Optional<DatasetVersion> findByDatasetIdAndVersionNumber(Long datasetId, Integer versionNumber);
    Optional<DatasetVersion> findTopByDatasetIdOrderByVersionNumberDesc(Long datasetId);
}
