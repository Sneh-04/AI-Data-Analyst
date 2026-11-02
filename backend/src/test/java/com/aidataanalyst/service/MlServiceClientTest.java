package com.aidataanalyst.service;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.HttpStatus;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.content;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class MlServiceClientTest {

    @Test
    void postsEphemeralInferencePayloadToPooledRouteWithInternalAuthentication() {
        String internalKey = "0123456789abcdef0123456789abcdef";
        MlServiceClient client = new MlServiceClient(new RestTemplate());
        ReflectionTestUtils.setField(client, "mlServiceBaseUrl", "http://ml.test");
        ReflectionTestUtils.setField(client, "internalApiKey", internalKey);
        RestTemplate inferenceClient =
                (RestTemplate) ReflectionTestUtils.getField(client, "inferenceRestTemplate");
        MockRestServiceServer server = MockRestServiceServer.createServer(inferenceClient);
        Map<String, Object> payload = Map.of(
                "records", List.of(Map.of("target", 1.0)),
                "target_column", "target",
                "estimand", "mean",
                "m", 2,
                "seed", 42);
        server.expect(requestTo("http://ml.test/api/ml/inference/pooled"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(header("X-Internal-Key", internalKey))
                .andExpect(content().json(
                        "{\"records\":[{\"target\":1.0}],\"target_column\":\"target\","
                                + "\"estimand\":\"mean\",\"m\":2,\"seed\":42}"))
                .andRespond(withSuccess("{\"results\":[]}", MediaType.APPLICATION_JSON));

        Map<String, Object> response = client.runInference(payload);

        assertEquals(List.of(), response.get("results"));
        server.verify();
    }

    @Test
    void refusesToCallMlServiceWithoutAConfiguredInternalKey() {
        MlServiceClient client = new MlServiceClient(mock(RestTemplate.class));
        ReflectionTestUtils.setField(client, "mlServiceBaseUrl", "http://ml.test");

        assertThrows(IllegalStateException.class, () -> client.numericStats(Map.of("records", "sample")));
    }

    @Test
    void forwardsStatsRequestsToMatchingMlRoutes() {
        RestTemplate restTemplate = mock(RestTemplate.class);
        MlServiceClient client = new MlServiceClient(restTemplate);
        ReflectionTestUtils.setField(client, "mlServiceBaseUrl", "http://ml.test");
        ReflectionTestUtils.setField(client, "internalApiKey", "0123456789abcdef0123456789abcdef");
        Map<String, Object> body = Map.of("records", "sample");
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(Map.class)))
                .thenReturn(Map.of());

        client.numericStats(body);
        client.categoricalStats(body);
        client.correlationStats(body);

        verify(restTemplate).postForObject(
                eq("http://ml.test/api/ml/stats/numeric"), any(HttpEntity.class), eq(Map.class));
        verify(restTemplate).postForObject(
                eq("http://ml.test/api/ml/stats/categorical"), any(HttpEntity.class), eq(Map.class));
        verify(restTemplate).postForObject(
                eq("http://ml.test/api/ml/stats/correlation"), any(HttpEntity.class), eq(Map.class));
    }

    @Test
    void mapsMlServerErrorsToBadGateway() {
        RestTemplate restTemplate = mock(RestTemplate.class);
        MlServiceClient client = new MlServiceClient(restTemplate);
        ReflectionTestUtils.setField(client, "mlServiceBaseUrl", "http://ml.test");
        ReflectionTestUtils.setField(client, "internalApiKey", "0123456789abcdef0123456789abcdef");
        when(restTemplate.postForObject(anyString(), any(HttpEntity.class), eq(Map.class)))
                .thenThrow(HttpServerErrorException.create(
                        HttpStatus.INTERNAL_SERVER_ERROR, "error", HttpHeaders.EMPTY, new byte[0], null));

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> client.numericStats(Map.of("records", "sample")));

        assertEquals(HttpStatus.BAD_GATEWAY, exception.getStatusCode());
    }
}
