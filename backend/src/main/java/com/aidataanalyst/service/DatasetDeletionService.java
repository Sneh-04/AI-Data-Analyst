package com.aidataanalyst.service;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;

@Service
public class DatasetDeletionService {

    private final DatasetDeletionTransactionService transactionService;
    private final DatasetStorageService storageService;

    public DatasetDeletionService(
            DatasetDeletionTransactionService transactionService,
            DatasetStorageService storageService) {
        this.transactionService = transactionService;
        this.storageService = storageService;
    }

    public void delete(Long datasetId, String email) {
        DatasetDeletionTransactionService.DeletionPlan plan = transactionService.prepare(datasetId, email);

        IOException deletionFailure = null;
        for (String storagePath : plan.storagePaths()) {
            try {
                storageService.delete(storagePath);
            } catch (IOException exception) {
                if (deletionFailure == null) {
                    deletionFailure = new IOException("One or more dataset files could not be deleted");
                }
                deletionFailure.addSuppressed(exception);
            }
        }
        if (deletionFailure != null) {
            transactionService.markFailed(plan.jobId());
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Dataset deletion is incomplete. Retry the delete request to continue.",
                    deletionFailure);
        }

        transactionService.complete(plan);
    }
}
