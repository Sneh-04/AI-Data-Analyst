package com.aidataanalyst.service;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.DatasetVersion;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.DatasetVersionRepository;
import com.aidataanalyst.repository.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class VersioningService {

    private final DatasetRepository datasetRepository;
    private final DatasetVersionRepository versionRepository;
    private final DatasetStorageService storageService;
    private final UserRepository userRepository;

    public VersioningService(DatasetRepository datasetRepository, DatasetVersionRepository versionRepository,
                             DatasetStorageService storageService, UserRepository userRepository) {
        this.datasetRepository = datasetRepository;
        this.versionRepository = versionRepository;
        this.storageService = storageService;
        this.userRepository = userRepository;
    }

    @Transactional
    public DatasetVersion saveVersion(Long datasetId, Map<String, Object> request,
                                      Map<String, Object> cleaningResult, String email) {
        Dataset dataset = getDataset(datasetId);
        User user = userRepository.findByEmailIgnoreCase(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "User is unavailable"));
        Object rawRecords = cleaningResult.get("cleaned_records");
        if (!(rawRecords instanceof List<?>)) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Cleaning response has no records");
        }
        List<Map<String, Object>> records = toRecords((List<?>) rawRecords);
        int nextVersion = versionRepository.findTopByDatasetIdOrderByVersionNumberDesc(datasetId)
                .map(version -> version.getVersionNumber() + 1)
                .orElse(1);
        String storagePath = "dataset-" + datasetId + "-version-" + nextVersion + ".csv";
        try {
            storageService.writeRecords(storagePath, records);
        } catch (IOException exception) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Unable to store dataset version", exception);
        }

        Map<String, Object> operationParams = new LinkedHashMap<>(request);
        operationParams.remove("records");
        @SuppressWarnings("unchecked")
        Map<String, Object> summary = cleaningResult.get("summary") instanceof Map<?, ?>
                ? (Map<String, Object>) cleaningResult.get("summary")
                : Map.of();
        String operation = "clean:" + String.valueOf(request.getOrDefault("outlier_method", "none"));
        return versionRepository.save(new DatasetVersion(
                dataset.getId(), nextVersion, storagePath, operation,
                operationParams, summary, user.getId()));
    }

    @Transactional(readOnly = true)
    public List<DatasetVersion> listVersions(Long datasetId) {
        getDataset(datasetId);
        return versionRepository.findByDatasetIdOrderByVersionNumberDesc(datasetId);
    }

    @Transactional
    public Map<String, Object> restore(Long datasetId, Integer versionNumber) {
        Dataset dataset = getDataset(datasetId);
        DatasetVersion version = versionRepository.findByDatasetIdAndVersionNumber(datasetId, versionNumber)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset version not found"));
        List<Map<String, Object>> records = storageService.readRecordsFromPath(version.getStoragePath());
        try {
            storageService.writeRecords(dataset.getStoragePath(), records);
        } catch (IOException exception) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Unable to restore dataset version", exception);
        }
        return Map.of("versionNumber", versionNumber, "records", records);
    }

    private Dataset getDataset(Long datasetId) {
        return datasetRepository.findById(datasetId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset not found"));
    }

    private List<Map<String, Object>> toRecords(List<?> rawRecords) {
        List<Map<String, Object>> records = new ArrayList<>();
        for (Object rawRecord : rawRecords) {
            if (!(rawRecord instanceof Map<?, ?> rawMap)) {
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Cleaning response contains an invalid record");
            }
            Map<String, Object> record = new LinkedHashMap<>();
            rawMap.forEach((key, value) -> record.put(String.valueOf(key), value));
            records.add(record);
        }
        return records;
    }
}
