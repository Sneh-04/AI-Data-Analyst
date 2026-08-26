package com.aidataanalyst.controller;

import com.aidataanalyst.service.MlServiceClient;
import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.service.DatasetStorageService;
import com.aidataanalyst.service.VersioningService;
import com.aidataanalyst.service.ReportGenerationService;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Gateway endpoints consumed by the React frontend. Real implementation
 * would also: load/save dataset rows + versions via JPA repositories,
 * write to audit_log, and enforce workspace membership via Spring Security.
 * Wiring shown here is intentionally minimal so the request path
 * (React -> Spring Boot -> FastAPI -> Postgres) is clear end to end.
 */
@RestController
@RequestMapping("/api/datasets")
public class DatasetController {

    private final MlServiceClient mlServiceClient;
    private final DatasetRepository datasetRepository;
    private final DatasetStorageService datasetStorageService;
    private final VersioningService versioningService;
    private final ReportGenerationService reportGenerationService;

    public DatasetController(MlServiceClient mlServiceClient, DatasetRepository datasetRepository,
                             DatasetStorageService datasetStorageService, VersioningService versioningService,
                             ReportGenerationService reportGenerationService) {
        this.mlServiceClient = mlServiceClient;
        this.datasetRepository = datasetRepository;
        this.datasetStorageService = datasetStorageService;
        this.versioningService = versioningService;
        this.reportGenerationService = reportGenerationService;
    }

    @PostMapping("/{id}/clean")
    public Map<String, Object> clean(@PathVariable Long id, @RequestBody Map<String, Object> request) {
        // TODO: load dataset {id} from storage, merge into request, persist result as new dataset_version
        Map<String, Object> result = mlServiceClient.cleanDataset(request);
        versioningService.saveVersion(id, request, result,
            org.springframework.security.core.context.SecurityContextHolder.getContext()
                .getAuthentication().getName());
        return result;
    }

    @PostMapping("/{id}/health-score")
    public Map<String, Object> healthScore(@PathVariable Long id, @RequestBody Map<String, Object> request) {
        return mlServiceClient.healthScore(request);
    }

    @PostMapping("/{id}/forecast")
    public Map<String, Object> forecast(@PathVariable Long id, @RequestBody Map<String, Object> request) {
        // TODO: persist result into forecasts table
        return mlServiceClient.runForecast(request);
    }

    @PostMapping("/{id}/insights")
    public Map<String, Object> insights(@PathVariable Long id, @RequestBody Map<String, Object> request) {
        return mlServiceClient.generateInsights(request);
    }

    @PostMapping("/{id}/chat")
    public Map<String, Object> chat(@PathVariable Long id, @RequestBody Map<String, Object> request) {
        // TODO: persist user + assistant messages into chat_messages
        Map<String, Object> chatRequest = new HashMap<>(request);
        chatRequest.put("dataset_id", id);
        return mlServiceClient.chat(chatRequest);
    }

    @GetMapping("/{id}/records")
    public java.util.List<Map<String, Object>> records(@PathVariable Long id) {
        Dataset dataset = datasetRepository.findById(id)
                .orElseThrow(() -> new org.springframework.web.server.ResponseStatusException(
                        org.springframework.http.HttpStatus.NOT_FOUND, "Dataset not found"));
        return datasetStorageService.readRecords(dataset);
    }

    @GetMapping("/{id}/versions")
    public List<com.aidataanalyst.entity.DatasetVersion> versions(@PathVariable Long id) {
        return versioningService.listVersions(id);
    }

    @PostMapping("/{id}/versions/{versionNumber}/restore")
    public Map<String, Object> restore(@PathVariable Long id, @PathVariable Integer versionNumber) {
        return versioningService.restore(id, versionNumber);
    }

    @PostMapping("/{id}/reports")
    public ResponseEntity<ByteArrayResource> generateReport(@PathVariable Long id,
                                                            @RequestBody Map<String, Object> request,
                                                            Authentication authentication) {
        return reportGenerationService.generate(id, (String) request.get("format"), authentication.getName());
    }
}
