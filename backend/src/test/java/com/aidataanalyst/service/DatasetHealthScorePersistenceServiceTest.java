package com.aidataanalyst.service;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.DatasetHealthScore;
import com.aidataanalyst.repository.DatasetHealthScoreRepository;
import com.aidataanalyst.repository.DatasetRepository;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DatasetHealthScorePersistenceServiceTest {

    @Test
    void updatesLatestScoreAndAppendsAnAssessment() {
        DatasetRepository datasetRepository = mock(DatasetRepository.class);
        DatasetHealthScoreRepository historyRepository = mock(DatasetHealthScoreRepository.class);
        Dataset dataset = new Dataset(3L, 42L, "sample.csv", "sample.csv", 10, 2);
        when(datasetRepository.findById(17L)).thenReturn(Optional.of(dataset));
        DatasetHealthScorePersistenceService service =
                new DatasetHealthScorePersistenceService(datasetRepository, historyRepository);

        service.recordAssessment(17L, 92, "A (Excellent)");

        assertEquals(92, dataset.getHealthScore());
        verify(datasetRepository).save(dataset);
        ArgumentCaptor<DatasetHealthScore> assessment = ArgumentCaptor.forClass(DatasetHealthScore.class);
        verify(historyRepository).save(assessment.capture());
        assertEquals(92, assessment.getValue().getScore());
        assertEquals("A (Excellent)", assessment.getValue().getGrade());
        assertNotNull(assessment.getValue().getAssessedAt());
    }
}
