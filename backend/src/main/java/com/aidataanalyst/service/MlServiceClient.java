package com.aidataanalyst.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

/**
 * Thin client for the Python FastAPI ML microservice.
 * Spring Boot never runs pandas/sklearn itself — it authenticates the user,
 * loads the dataset from storage, forwards it here as JSON, persists the
 * result, and returns it to React. Keeps the ML service stateless and
 * independently scalable.
 */
@Service
public class MlServiceClient {

    private final RestTemplate restTemplate;

    @Value("${ml.service.base-url:http://localhost:8000}")
    private String mlServiceBaseUrl;

    public MlServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Map<String, Object> post(String path, Map<String, Object> body) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);
        return restTemplate.postForObject(mlServiceBaseUrl + path, entity, Map.class);
    }

    public Map<String, Object> cleanDataset(Map<String, Object> body) {
        return post("/api/ml/cleaning/clean", body);
    }

    public Map<String, Object> healthScore(Map<String, Object> body) {
        return post("/api/ml/health/score", body);
    }

    public Map<String, Object> runForecast(Map<String, Object> body) {
        return post("/api/ml/forecasting/run", body);
    }

    public Map<String, Object> generateInsights(Map<String, Object> body) {
        return post("/api/ml/insights/generate", body);
    }

    public Map<String, Object> chat(Map<String, Object> body) {
        return post("/api/ml/chat/ask", body);
    }
}
