package com.aidataanalyst.repository;

import com.aidataanalyst.entity.DatasetHealthScore;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface DatasetHealthScoreRepository extends JpaRepository<DatasetHealthScore, Long> {
    Optional<DatasetHealthScore> findTopByDataset_IdOrderByAssessedAtDescIdDesc(Long datasetId);

    List<DatasetHealthScore> findTop100ByDataset_IdOrderByAssessedAtDescIdDesc(Long datasetId);
}
