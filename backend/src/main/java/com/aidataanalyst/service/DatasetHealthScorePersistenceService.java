package com.aidataanalyst.service;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.DatasetHealthScore;
import com.aidataanalyst.repository.DatasetHealthScoreRepository;
import com.aidataanalyst.repository.DatasetRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class DatasetHealthScorePersistenceService {

    private final DatasetRepository datasetRepository;
    private final DatasetHealthScoreRepository healthScoreRepository;

    public DatasetHealthScorePersistenceService(DatasetRepository datasetRepository,
                                                DatasetHealthScoreRepository healthScoreRepository) {
        this.datasetRepository = datasetRepository;
        this.healthScoreRepository = healthScoreRepository;
    }

    @Transactional
    public void recordAssessment(Long datasetId, int score, String grade) {
        Dataset dataset = datasetRepository.findById(datasetId)
                .orElseThrow(() -> new IllegalStateException("Dataset disappeared during health assessment"));
        dataset.setHealthScore(score);
        datasetRepository.save(dataset);
        healthScoreRepository.save(new DatasetHealthScore(dataset, score, grade));
    }
}
