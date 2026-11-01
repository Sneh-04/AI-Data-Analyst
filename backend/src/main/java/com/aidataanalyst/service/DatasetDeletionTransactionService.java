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
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.ArrayList;
import java.util.List;

@Service
public class DatasetDeletionTransactionService {

    private final DatasetRepository datasetRepository;
    private final DatasetVersionRepository versionRepository;
    private final ReportRepository reportRepository;
    private final DatasetDeletionJobRepository deletionJobRepository;
    private final UserRepository userRepository;

    public DatasetDeletionTransactionService(
            DatasetRepository datasetRepository,
            DatasetVersionRepository versionRepository,
            ReportRepository reportRepository,
            DatasetDeletionJobRepository deletionJobRepository,
            UserRepository userRepository) {
        this.datasetRepository = datasetRepository;
        this.versionRepository = versionRepository;
        this.reportRepository = reportRepository;
        this.deletionJobRepository = deletionJobRepository;
        this.userRepository = userRepository;
    }

    @Transactional
    public DeletionPlan prepare(Long datasetId, String email) {
        User user = userRepository.findByEmailIgnoreCase(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "User is unavailable"));

        Dataset dataset = datasetRepository.findOwnedByIdForUpdate(datasetId, user.getId())
                .orElse(null);
        if (dataset == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset not found");
        }

        DatasetDeletionJob job = deletionJobRepository.findByDatasetId(datasetId).orElse(null);
        if (job != null && !job.getRequestedById().equals(user.getId())) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset not found");
        }
        if (job == null) {
            job = deletionJobRepository.save(new DatasetDeletionJob(datasetId, user.getId()));
        }
        dataset.markDeletionPending();
        job.markInProgress();
        datasetRepository.saveAndFlush(dataset);
        deletionJobRepository.saveAndFlush(job);

        List<String> paths = new ArrayList<>();
        paths.add(dataset.getStoragePath());
        for (DatasetVersion version : versionRepository.findAllByDatasetId(datasetId)) {
            paths.add(version.getStoragePath());
        }
        for (Report report : reportRepository.findAllByDatasetId(datasetId)) {
            paths.add(report.getStoragePath());
        }
        return new DeletionPlan(job.getId(), datasetId, paths.stream().distinct().toList());
    }

    @Transactional
    public void markFailed(Long jobId) {
        DatasetDeletionJob job = deletionJobRepository.findById(jobId)
                .orElseThrow(() -> new IllegalStateException("Dataset deletion record is unavailable"));
        job.markFailed();
    }

    @Transactional
    public void complete(DeletionPlan plan) {
        DatasetDeletionJob job = deletionJobRepository.findById(plan.jobId())
                .orElseThrow(() -> new IllegalStateException("Dataset deletion record is unavailable"));
        Dataset dataset = datasetRepository.findOwnedByIdForUpdate(plan.datasetId(), job.getRequestedById())
                .orElse(null);
        if (dataset != null) {
            if (!"DELETING".equals(dataset.getDeletionStatus())) {
                throw new IllegalStateException("Dataset deletion was not prepared");
            }
            datasetRepository.delete(dataset);
        }
        job.markCompleted();
        deletionJobRepository.save(job);
    }

    public record DeletionPlan(Long jobId, Long datasetId, List<String> storagePaths) {
    }
}
