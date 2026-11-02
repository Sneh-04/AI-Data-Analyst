package com.aidataanalyst.controller;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.repository.DatasetHealthScoreRepository;
import com.aidataanalyst.service.ChatPersistenceService;
import com.aidataanalyst.service.DatasetAccessService;
import com.aidataanalyst.service.DatasetDeletionService;
import com.aidataanalyst.service.DatasetHealthScorePersistenceService;
import com.aidataanalyst.service.DatasetStorageService;
import com.aidataanalyst.service.ForecastPersistenceService;
import com.aidataanalyst.service.MlServiceClient;
import com.aidataanalyst.service.ReportGenerationService;
import com.aidataanalyst.service.VersioningService;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.Authentication;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DatasetListControllerTest {

    @Test
    void listsOnlyDatasetsOwnedByTheAuthenticatedUser() {
        DatasetAccessService datasetAccessService = mock(DatasetAccessService.class);
        DatasetController controller = new DatasetController(
                mock(MlServiceClient.class),
                mock(DatasetHealthScoreRepository.class),
                datasetAccessService,
                mock(DatasetDeletionService.class),
                mock(DatasetHealthScorePersistenceService.class),
                mock(DatasetStorageService.class),
                mock(VersioningService.class),
                mock(ReportGenerationService.class),
                mock(ForecastPersistenceService.class),
                mock(ChatPersistenceService.class));
        Authentication authentication = mock(Authentication.class);
        when(authentication.getName()).thenReturn("analyst@example.test");
        Dataset dataset = mock(Dataset.class);
        when(dataset.getId()).thenReturn(23L);
        when(dataset.getFileName()).thenReturn("sales.csv");
        when(dataset.getRowCount()).thenReturn(12);
        when(dataset.getColumnCount()).thenReturn(3);
        when(datasetAccessService.listOwnedDatasets("analyst@example.test")).thenReturn(List.of(dataset));

        List<DatasetController.DatasetSummary> actual = controller.listDatasets(authentication);

        assertEquals(List.of(new DatasetController.DatasetSummary(23L, "sales.csv", 12, 3, null)), actual);
        verify(datasetAccessService).listOwnedDatasets("analyst@example.test");
    }
}
