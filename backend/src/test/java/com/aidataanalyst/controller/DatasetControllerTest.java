package com.aidataanalyst.controller;

import com.aidataanalyst.repository.DatasetHealthScoreRepository;
import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.service.ChatPersistenceService;
import com.aidataanalyst.service.DatasetAccessService;
import com.aidataanalyst.service.DatasetDeletionService;
import com.aidataanalyst.service.DatasetHealthScorePersistenceService;
import com.aidataanalyst.service.DatasetStorageService;
import com.aidataanalyst.service.ForecastPersistenceService;
import com.aidataanalyst.service.MlServiceClient;
import com.aidataanalyst.service.ReportGenerationService;
import com.aidataanalyst.service.VersioningService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.server.ResponseStatusException;

import java.util.Map;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentCaptor.forClass;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DatasetControllerTest {

    private MlServiceClient mlServiceClient;
    private DatasetAccessService datasetAccessService;
    private DatasetDeletionService datasetDeletionService;
    private DatasetStorageService datasetStorageService;
    private ReportGenerationService reportGenerationService;
    private DatasetController controller;
    private Authentication authentication;

    @BeforeEach
    void setUp() {
        mlServiceClient = mock(MlServiceClient.class);
        datasetAccessService = mock(DatasetAccessService.class);
        datasetDeletionService = mock(DatasetDeletionService.class);
        datasetStorageService = mock(DatasetStorageService.class);
        reportGenerationService = mock(ReportGenerationService.class);
        controller = new DatasetController(
                mlServiceClient,
                mock(DatasetHealthScoreRepository.class),
                datasetAccessService,
                datasetDeletionService,
                mock(DatasetHealthScorePersistenceService.class),
                datasetStorageService,
                mock(VersioningService.class),
                reportGenerationService,
                mock(ForecastPersistenceService.class),
                mock(ChatPersistenceService.class));
        authentication = mock(Authentication.class);
        when(authentication.getName()).thenReturn("analyst@example.test");
    }

    @Test
    void datasetDeletionPassesAuthenticatedOwnerAndDatasetIdToDeletionService() {
        var response = controller.deleteDataset(17L, authentication);

        assertEquals(HttpStatus.NO_CONTENT, response.getStatusCode());
        verify(datasetDeletionService).delete(17L, "analyst@example.test");
    }

    @Test
    void datasetDeletionDoesNotProceedWhenAuthenticatedUserIsNotTheOwner() {
        org.mockito.Mockito.doThrow(new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset not found"))
                .when(datasetDeletionService).delete(17L, "analyst@example.test");

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> controller.deleteDataset(17L, authentication));

        assertEquals(HttpStatus.NOT_FOUND, exception.getStatusCode());
        verify(datasetDeletionService).delete(17L, "analyst@example.test");
    }

    @Test
    void inferenceUsesAuthorizedStoredRowsAndReturnsMlResponseUnchanged() {
        Dataset dataset = new Dataset(1L, 42L, "source.csv", "datasets/source.csv", 2, 1);
        List<Map<String, Object>> storedRows = List.of(
                Map.of("outcome", 1.0),
                Map.of("outcome", 2.0));
        Map<String, Object> request = Map.of(
                "target_column", "outcome",
                "estimand", "mean",
                "m", 3,
                "seed", 42);
        Map<String, Object> expectedPayload = Map.of(
                "records", storedRows,
                "target_column", "outcome",
                "estimand", "mean",
                "m", 3,
                "seed", 42);
        Map<String, Object> response = Map.of("predictions", "result");
        when(datasetAccessService.requireOwnedDataset(17L, "analyst@example.test")).thenReturn(dataset);
        when(datasetStorageService.readRecords(dataset)).thenReturn(storedRows);
        when(mlServiceClient.runInference(expectedPayload)).thenReturn(response);

        Map<String, Object> actual = controller.inference(17L, request, authentication);

        assertSame(response, actual);
        verify(datasetAccessService).requireOwnedDataset(17L, "analyst@example.test");
        verify(datasetStorageService).readRecords(dataset);
        verify(mlServiceClient).runInference(expectedPayload);
    }

    @Test
    void inferenceRejectsClientSuppliedRows() {
        Dataset dataset = new Dataset(1L, 42L, "source.csv", "datasets/source.csv", 2, 1);
        when(datasetAccessService.requireOwnedDataset(17L, "analyst@example.test")).thenReturn(dataset);
        Map<String, Object> request = Map.of(
                "target_column", "outcome",
                "records", List.of(Map.of("outcome", 999.0)));

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> controller.inference(17L, request, authentication));

        assertEquals(HttpStatus.BAD_REQUEST, exception.getStatusCode());
        org.mockito.Mockito.verifyNoInteractions(mlServiceClient, datasetStorageService);
    }

    @Test
    void inferenceRejectsUnsupportedSettings() {
        Dataset dataset = new Dataset(1L, 42L, "source.csv", "datasets/source.csv", 2, 1);
        when(datasetAccessService.requireOwnedDataset(17L, "analyst@example.test")).thenReturn(dataset);

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> controller.inference(
                        17L,
                        Map.of("target_column", "outcome", "dataset_id", 999L),
                        authentication));

        assertEquals(HttpStatus.BAD_REQUEST, exception.getStatusCode());
        org.mockito.Mockito.verifyNoInteractions(mlServiceClient, datasetStorageService);
    }

    @Test
    void inferenceRejectsBlankTargetColumn() {
        Map<String, Object> request = Map.of("target_column", "  ");

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> controller.inference(17L, request, authentication));

        assertEquals(HttpStatus.BAD_REQUEST, exception.getStatusCode());
    }

    @Test
    void inferenceReturnsNotFoundForDatasetNotOwnedByUser() {
        when(datasetAccessService.requireOwnedDataset(17L, "analyst@example.test"))
                .thenThrow(new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset not found"));

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> controller.inference(17L, Map.of("target_column", "outcome"), authentication));

        assertEquals(HttpStatus.NOT_FOUND, exception.getStatusCode());
    }

    @Test
    void inferencePreservesMlBadGatewayError() {
        Dataset dataset = new Dataset(1L, 42L, "source.csv", "datasets/source.csv", 2, 1);
        Map<String, Object> request = Map.of("target_column", "outcome");
        List<Map<String, Object>> storedRows = List.of(Map.of("outcome", 1.0));
        Map<String, Object> expectedPayload = Map.of(
                "records", storedRows,
                "target_column", "outcome");
        when(datasetAccessService.requireOwnedDataset(17L, "analyst@example.test")).thenReturn(dataset);
        when(datasetStorageService.readRecords(dataset)).thenReturn(storedRows);
        when(mlServiceClient.runInference(expectedPayload))
                .thenThrow(new ResponseStatusException(HttpStatus.BAD_GATEWAY, "ML service rejected the request."));

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> controller.inference(17L, request, authentication));

        assertEquals(HttpStatus.BAD_GATEWAY, exception.getStatusCode());
    }

    @Test
    void statsEndpointsForwardRequestAfterOwnershipCheck() {
        Map<String, Object> request = Map.of("records", "sample");

        controller.numericStats(17L, request, authentication);
        controller.categoricalStats(17L, request, authentication);
        controller.correlationStats(17L, request, authentication);

        verify(datasetAccessService, org.mockito.Mockito.times(3))
                .requireOwnedDataset(17L, "analyst@example.test");
        verify(mlServiceClient).numericStats(request);
        verify(mlServiceClient).categoricalStats(request);
        verify(mlServiceClient).correlationStats(request);
    }

    @Test
    void chatUsesTheAuthorizedPathDatasetInsteadOfAClientSuppliedDatasetId() {
        Map<String, Object> request = Map.of(
                "dataset_id", 999L,
                "question", "Summarize this dataset");
        when(mlServiceClient.chat(org.mockito.ArgumentMatchers.anyMap()))
                .thenReturn(Map.of("answer", "Summary"));

        controller.chat(17L, request, authentication);

        var forwarded = forClass(Map.class);
        verify(mlServiceClient).chat(forwarded.capture());
        assertEquals(17L, forwarded.getValue().get("dataset_id"));
        verify(datasetAccessService).requireOwnedDataset(17L, "analyst@example.test");
    }

    @Test
    void reportGenerationDoesNotProceedWhenTheDatasetIsNotOwned() {
        when(datasetAccessService.requireOwnedDataset(17L, "analyst@example.test"))
                .thenThrow(new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset not found"));

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> controller.generateReport(17L, Map.of("format", "PDF"), authentication));

        assertEquals(HttpStatus.NOT_FOUND, exception.getStatusCode());
        verify(reportGenerationService, org.mockito.Mockito.never())
                .generate(17L, "PDF", "analyst@example.test");
    }
}
