package com.aidataanalyst.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DatasetDeletionServiceTest {

    @TempDir
    Path storageRoot;

    @Test
    void deletesOriginalVersionAndReportFilesBeforeCompletingDatabaseDeletion() throws Exception {
        DatasetDeletionTransactionService transactionService =
                mock(DatasetDeletionTransactionService.class);
        DatasetDeletionTransactionService.DeletionPlan plan =
                new DatasetDeletionTransactionService.DeletionPlan(
                        91L, 17L, List.of("original.csv", "dataset-17-version-1.csv", "reports/report.pdf"));
        when(transactionService.prepare(17L, "owner@example.test")).thenReturn(plan);
        for (String relativePath : plan.storagePaths()) {
            Path file = storageRoot.resolve(relativePath);
            Files.createDirectories(file.getParent());
            Files.writeString(file, "sensitive data");
        }
        DatasetDeletionService service = new DatasetDeletionService(
                transactionService, new DatasetStorageService(storageRoot.toString()));

        service.delete(17L, "owner@example.test");

        for (String relativePath : plan.storagePaths()) {
            assertFalse(Files.exists(storageRoot.resolve(relativePath)));
        }
        verify(transactionService).complete(plan);
    }

    @Test
    void keepsDeletionRetryableAndReportsFailureWhenAStoragePathIsInvalid() {
        DatasetDeletionTransactionService transactionService =
                mock(DatasetDeletionTransactionService.class);
        DatasetDeletionTransactionService.DeletionPlan plan =
                new DatasetDeletionTransactionService.DeletionPlan(92L, 18L, List.of("../outside.csv"));
        when(transactionService.prepare(18L, "owner@example.test")).thenReturn(plan);
        DatasetDeletionService service = new DatasetDeletionService(
                transactionService, new DatasetStorageService(storageRoot.toString()));

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> service.delete(18L, "owner@example.test"));

        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, exception.getStatusCode());
        verify(transactionService).markFailed(92L);
    }

    @Test
    void repeatedDeletionOfACompletedDatasetReturnsNotFound() {
        DatasetDeletionTransactionService transactionService =
                mock(DatasetDeletionTransactionService.class);
        when(transactionService.prepare(19L, "owner@example.test"))
                .thenThrow(new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset not found"));
        DatasetDeletionService service = new DatasetDeletionService(
                transactionService, new DatasetStorageService(storageRoot.toString()));

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> service.delete(19L, "owner@example.test"));

        assertEquals(HttpStatus.NOT_FOUND, exception.getStatusCode());
        verify(transactionService).prepare(19L, "owner@example.test");
    }
}
