package com.aidataanalyst.controller;

import com.aidataanalyst.service.ResearchSummaryService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/research")
public class ResearchController {

    private final ResearchSummaryService researchSummaryService;

    public ResearchController(ResearchSummaryService researchSummaryService) {
        this.researchSummaryService = researchSummaryService;
    }

    @GetMapping("/v4/summary")
    public ResponseEntity<Map<String, Object>> getV4Summary() {
        Map<String, Object> summary = researchSummaryService.loadSummary();

        HttpHeaders headers = new HttpHeaders();
        headers.add("X-Research-Artifact-Version", "v4");
        headers.add("X-Research-Artifact-Checksum-Verified", "true");
        if (researchSummaryService.getLastResolvedArtifactPath() != null) {
            headers.add("X-Research-Artifact-Path", researchSummaryService.getLastResolvedArtifactPath());
        }
        if (researchSummaryService.getLastVerifiedSha256() != null) {
            headers.add("X-Research-Artifact-Sha256", researchSummaryService.getLastVerifiedSha256());
        }

        return ResponseEntity.ok().headers(headers).body(summary);
    }
}
