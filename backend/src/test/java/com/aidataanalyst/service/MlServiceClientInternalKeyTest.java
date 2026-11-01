package com.aidataanalyst.service;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpEntity;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;
import org.mockito.ArgumentCaptor;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class MlServiceClientInternalKeyTest {

    @Test
    void includesConfiguredInternalKeyOnMlRequests() {
        RestTemplate restTemplate = mock(RestTemplate.class);
        MlServiceClient client = new MlServiceClient(restTemplate);
        ReflectionTestUtils.setField(client, "mlServiceBaseUrl", "http://ml.test");
        ReflectionTestUtils.setField(client, "internalApiKey", "test-shared-key");
        when(restTemplate.postForObject(any(String.class), any(HttpEntity.class), eq(Map.class)))
                .thenReturn(Map.of());

        client.numericStats(Map.of("records", "sample"));

        ArgumentCaptor<HttpEntity> request = ArgumentCaptor.forClass(HttpEntity.class);
        verify(restTemplate).postForObject(
                eq("http://ml.test/api/ml/stats/numeric"),
                request.capture(),
                eq(Map.class));
        assertEquals("test-shared-key", request.getValue().getHeaders().getFirst("X-Internal-Key"));
    }
}
