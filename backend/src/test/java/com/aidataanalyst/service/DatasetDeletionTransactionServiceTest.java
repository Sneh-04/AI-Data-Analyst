package com.aidataanalyst.service;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.DatasetDeletionJob;
import com.aidataanalyst.entity.DatasetVersion;
import com.aidataanalyst.entity.Report;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.DatasetDeletionJobRepository;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.DatasetVersionRepository;
import com.aidataanalyst.repository.ReportRepository;
import com.aidataanalyst.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DatasetDeletionTransactionServiceTest {

    @Test
    void refusesDeletionWhenTheDatasetIsNotOwnedByTheAuthenticatedUser() {
        DatasetRepository datasetRepository = mock(DatasetRepository.class);
        DatasetDeletionJobRepository jobRepository = mock(DatasetDeletionJobRepository.class);
        UserRepository userRepository = mock(UserRepository.class);
        User user = mock(User.class);
        when(user.getId()).thenReturn(42L);
        when(userRepository.findByEmailIgnoreCase("customer-b@example.test")).thenReturn(Optional.of(user));
        when(datasetRepository.findOwnedByIdForUpdate(17L, 42L)).thenReturn(Optional.empty());
        DatasetDeletionTransactionService service = new DatasetDeletionTransactionService(
                datasetRepository,
                mock(DatasetVersionRepository.class),
                mock(ReportRepository.class),
                jobRepository,
                userRepository);

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> service.prepare(17L, "customer-b@example.test"));

        assertEquals(HttpStatus.NOT_FOUND, exception.getStatusCode());
        verify(datasetRepository).findOwnedByIdForUpdate(17L, 42L);
        verify(jobRepository, never()).save(any(DatasetDeletionJob.class));
    }

    @Test
    void deletionPlanIncludesAllDatabaseReferencedFiles() {
        DatasetRepository datasetRepository = mock(DatasetRepository.class);
        DatasetVersionRepository versionRepository = mock(DatasetVersionRepository.class);
        ReportRepository reportRepository = mock(ReportRepository.class);
        DatasetDeletionJobRepository jobRepository = mock(DatasetDeletionJobRepository.class);
        UserRepository userRepository = mock(UserRepository.class);
        User user = mock(User.class);
        Dataset dataset = mock(Dataset.class);
        DatasetDeletionJob job = mock(DatasetDeletionJob.class);
        when(user.getId()).thenReturn(42L);
        when(userRepository.findByEmailIgnoreCase("owner@example.test")).thenReturn(Optional.of(user));
        when(datasetRepository.findOwnedByIdForUpdate(17L, 42L)).thenReturn(Optional.of(dataset));
        when(dataset.getStoragePath()).thenReturn("upload.csv");
        when(versionRepository.findAllByDatasetId(17L))
                .thenReturn(List.of(new DatasetVersion(17L, 1, "version.csv", "clean:none", null, null, 42L)));
        when(reportRepository.findAllByDatasetId(17L))
                .thenReturn(List.of(new Report(17L, "PDF", "reports/report.pdf", 42L)));
        when(jobRepository.findByDatasetId(17L)).thenReturn(Optional.empty());
        when(jobRepository.save(any(DatasetDeletionJob.class))).thenReturn(job);
        when(job.getId()).thenReturn(91L);
        DatasetDeletionTransactionService service = new DatasetDeletionTransactionService(
                datasetRepository, versionRepository, reportRepository, jobRepository, userRepository);

        DatasetDeletionTransactionService.DeletionPlan plan =
                service.prepare(17L, "owner@example.test");

        assertEquals(List.of("upload.csv", "version.csv", "reports/report.pdf"), plan.storagePaths());
        verify(datasetRepository).findOwnedByIdForUpdate(17L, 42L);
        verify(dataset).markDeletionPending();
        verify(datasetRepository).saveAndFlush(dataset);
    }
}
