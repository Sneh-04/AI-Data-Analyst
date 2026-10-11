package com.aidataanalyst.controller;

import com.aidataanalyst.service.MlServiceClient;
import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.DatasetHealthScore;
import com.aidataanalyst.repository.DatasetHealthScoreRepository;
import com.aidataanalyst.service.DatasetAccessService;
import com.aidataanalyst.service.DatasetHealthScorePersistenceService;
import com.aidataanalyst.service.DatasetStorageService;
import com.aidataanalyst.service.VersioningService;
import com.aidataanalyst.service.ReportGenerationService;
import com.aidataanalyst.service.ForecastPersistenceService;
import com.aidataanalyst.service.ChatPersistenceService;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Authenticated gateway endpoints consumed by the React frontend.
 */
@RestController
@RequestMapping("/api/datasets")
public class DatasetController {

    private final MlServiceClient mlServiceClient;
    private final DatasetHealthScoreRepository healthScoreRepository;
    private final DatasetAccessService datasetAccessService;
    private final DatasetHealthScorePersistenceService healthScorePersistenceService;
    private final DatasetStorageService datasetStorageService;
    private final VersioningService versioningService;
    private final ReportGenerationService reportGenerationService;
    private final ForecastPersistenceService forecastPersistenceService;
    private final ChatPersistenceService chatPersistenceService;

    public DatasetController(MlServiceClient mlServiceClient, DatasetHealthScoreRepository healthScoreRepository,
                             DatasetAccessService datasetAccessService,
                             DatasetHealthScorePersistenceService healthScorePersistenceService,
                             DatasetStorageService datasetStorageService, VersioningService versioningService,
                             ReportGenerationService reportGenerationService,
                             ForecastPersistenceService forecastPersistenceService,
                             ChatPersistenceService chatPersistenceService) {
        this.mlServiceClient = mlServiceClient;
        this.healthScoreRepository = healthScoreRepository;
        this.datasetAccessService = datasetAccessService;
        this.healthScorePersistenceService = healthScorePersistenceService;
        this.datasetStorageService = datasetStorageService;
        this.versioningService = versioningService;
        this.reportGenerationService = reportGenerationService;
        this.forecastPersistenceService = forecastPersistenceService;
        this.chatPersistenceService = chatPersistenceService;
    }

    @PostMapping("/{id}/clean")
    public Map<String, Object> clean(@PathVariable Long id, @RequestBody Map<String, Object> request,
                                     Authentication authentication) {
        datasetAccessService.requireOwnedDataset(id, authentication.getName());
        Map<String, Object> result = mlServiceClient.cleanDataset(request);
        versioningService.saveVersion(id, request, result, authentication.getName());
        return result;
    }

    @PostMapping("/{id}/health-score")
    public Map<String, Object> healthScore(@PathVariable Long id, @RequestBody Map<String, Object> request,
                                          Authentication authentication) {
        Dataset dataset = datasetAccessService.requireOwnedDataset(id, authentication.getName());
        Integer previousScore = healthScoreRepository.findTopByDataset_IdOrderByAssessedAtDescIdDesc(id)
                .map(DatasetHealthScore::getScore)
                .orElse(dataset.getHealthScore());
        Map<String, Object> payload = new HashMap<>(request);
        if (previousScore != null) {
            payload.put("previous_score", previousScore);
        } else {
            payload.remove("previous_score");
        }
        Map<String, Object> result = mlServiceClient.healthScore(payload);
        if (!(result.get("score") instanceof Number score) || !(result.get("grade") instanceof String grade)
                || score.intValue() < 0 || score.intValue() > 100) {
            throw new org.springframework.web.server.ResponseStatusException(
                    org.springframework.http.HttpStatus.BAD_GATEWAY, "ML service returned an invalid health score");
        }
        healthScorePersistenceService.recordAssessment(id, score.intValue(), grade);
        return result;
    }

    @GetMapping("/{id}/health-score/history")
    public List<DatasetHealthScore> healthScoreHistory(@PathVariable Long id, Authentication authentication) {
        datasetAccessService.requireOwnedDataset(id, authentication.getName());
        return healthScoreRepository.findTop100ByDataset_IdOrderByAssessedAtDescIdDesc(id);
    }

    @PostMapping("/{id}/forecast")
    public Map<String, Object> forecast(@PathVariable Long id, @RequestBody Map<String, Object> request,
                                        Authentication authentication) {
        datasetAccessService.requireOwnedDataset(id, authentication.getName());
        Map<String, Object> result = mlServiceClient.runForecast(request);
        forecastPersistenceService.saveForecast(id, (String) request.get("date_column"),
                (String) request.get("value_column"), result, authentication.getName());
        return result;
    }

    @PostMapping("/{id}/insights")
    public Map<String, Object> insights(@PathVariable Long id, @RequestBody Map<String, Object> request,
                                        Authentication authentication) {
        datasetAccessService.requireOwnedDataset(id, authentication.getName());
        return mlServiceClient.generateInsights(request);
    }

    @PostMapping("/{id}/chat")
    public Map<String, Object> chat(@PathVariable Long id, @RequestBody Map<String, Object> request,
                                    Authentication authentication) {
        datasetAccessService.requireOwnedDataset(id, authentication.getName());
        Map<String, Object> chatRequest = new HashMap<>(request);
        chatRequest.put("dataset_id", id);
        Map<String, Object> result = mlServiceClient.chat(chatRequest);
        chatPersistenceService.recordExchange(id, (String) request.get("question"),
                (String) result.get("answer"), authentication.getName());
        return result;
    }

    @GetMapping("/{id}/records")
    public java.util.List<Map<String, Object>> records(@PathVariable Long id, Authentication authentication) {
        Dataset dataset = datasetAccessService.requireOwnedDataset(id, authentication.getName());
        return datasetStorageService.readRecords(dataset);
    }

    @GetMapping("/{id}/versions")
    public List<com.aidataanalyst.entity.DatasetVersion> versions(@PathVariable Long id,
                                                                  Authentication authentication) {
        datasetAccessService.requireOwnedDataset(id, authentication.getName());
        return versioningService.listVersions(id);
    }

    @PostMapping("/{id}/versions/{versionNumber}/restore")
    public Map<String, Object> restore(@PathVariable Long id, @PathVariable Integer versionNumber,
                                       Authentication authentication) {
        datasetAccessService.requireOwnedDataset(id, authentication.getName());
        return versioningService.restore(id, versionNumber);
    }

    @PostMapping("/{id}/reports")
    public ResponseEntity<ByteArrayResource> generateReport(@PathVariable Long id,
                                                            @RequestBody Map<String, Object> request,
                                                            Authentication authentication) {
        datasetAccessService.requireOwnedDataset(id, authentication.getName());
        return reportGenerationService.generate(id, (String) request.get("format"), authentication.getName());
    }
}
