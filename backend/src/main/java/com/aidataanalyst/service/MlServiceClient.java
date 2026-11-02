package com.aidataanalyst.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;
import org.springframework.stereotype.Service;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.server.ResponseStatusException;

import jakarta.annotation.PostConstruct;
import java.nio.charset.StandardCharsets;
import java.util.Map;

/**
 * Thin client for the Python FastAPI ML microservice.
 * Spring Boot never runs pandas/sklearn itself — it authenticates the user,
 * loads an authorized dataset from storage, and forwards analysis requests
 * here as JSON. Inference results are returned to React without persistence;
 * the ML service remains stateless and independently scalable.
 */
@Service
public class MlServiceClient {

    private final RestTemplate restTemplate;
    private final RestTemplate inferenceRestTemplate;

    @Value("${ml.service.base-url:http://localhost:8000}")
    private String mlServiceBaseUrl;

    @Value("${INTERNAL_API_KEY}")
    private String internalApiKey;

    public MlServiceClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(5_000);
        requestFactory.setReadTimeout(120_000);
        this.inferenceRestTemplate = new RestTemplate(requestFactory);
    }

    @PostConstruct
    void validateInternalApiKey() {
        requireInternalApiKey();
    }

    public Map<String, Object> post(String path, Map<String, Object> body) {
        return post(restTemplate, path, body);
    }

    private Map<String, Object> post(RestTemplate client, String path, Map<String, Object> body) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Internal-Key", requireInternalApiKey());
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);
        try {
            return client.postForObject(mlServiceBaseUrl + path, entity, Map.class);
        } catch (HttpStatusCodeException e) {
            HttpStatusCode status = e.getStatusCode().is4xxClientError()
                    ? e.getStatusCode()
                    : HttpStatus.BAD_GATEWAY;
            throw new ResponseStatusException(status, "ML service rejected the request.", e);
        } catch (ResourceAccessException e) {
            throw new ResponseStatusException(
                    HttpStatus.GATEWAY_TIMEOUT,
                    "ML service did not respond in time.",
                    e);
        }
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

    public Map<String, Object> runInference(Map<String, Object> body) {
        return post(inferenceRestTemplate, "/api/ml/inference/pooled", body);
    }

    public Map<String, Object> numericStats(Map<String, Object> body) {
        return post("/api/ml/stats/numeric", body);
    }

    public Map<String, Object> categoricalStats(Map<String, Object> body) {
        return post("/api/ml/stats/categorical", body);
    }

    public Map<String, Object> correlationStats(Map<String, Object> body) {
        return post("/api/ml/stats/correlation", body);
    }

    private String requireInternalApiKey() {
        if (internalApiKey == null
                || internalApiKey.getBytes(StandardCharsets.UTF_8).length < 32) {
            throw new IllegalStateException("INTERNAL_API_KEY must be configured with at least 32 bytes");
        }
        return internalApiKey;
    }
}
