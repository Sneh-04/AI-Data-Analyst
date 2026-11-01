package com.aidataanalyst.service;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.ReportRepository;
import com.aidataanalyst.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class ReportGenerationServiceTest {

    @Test
    void refusesToGenerateReportsForDatasetsNotOwnedByTheAuthenticatedUser() {
        DatasetRepository datasetRepository = mock(DatasetRepository.class);
        UserRepository userRepository = mock(UserRepository.class);
        User user = mock(User.class);
        when(user.getId()).thenReturn(42L);
        when(userRepository.findByEmailIgnoreCase("customer-b@example.test")).thenReturn(Optional.of(user));
        when(datasetRepository.findActiveOwnedByIdForUpdate(17L, 42L)).thenReturn(Optional.empty());
        RestTemplate restTemplate = mock(RestTemplate.class);
        ReportRepository reportRepository = mock(ReportRepository.class);
        ReportGenerationService service = new ReportGenerationService(
                datasetRepository,
                mock(DatasetStorageService.class),
                reportRepository,
                userRepository,
                restTemplate);

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> service.generate(17L, "PDF", "customer-b@example.test"));

        assertEquals(HttpStatus.NOT_FOUND, exception.getStatusCode());
        verify(restTemplate, never()).postForEntity(anyString(), any(HttpEntity.class), eq(byte[].class));
        verify(reportRepository, never()).save(any());
    }

    @Test
    void authenticatesMlReportRequestsWithTheInternalServiceKey() {
        DatasetRepository datasetRepository = mock(DatasetRepository.class);
        UserRepository userRepository = mock(UserRepository.class);
        User user = mock(User.class);
        Dataset dataset = mock(Dataset.class);
        DatasetStorageService storageService = mock(DatasetStorageService.class);
        RestTemplate restTemplate = mock(RestTemplate.class);
        when(user.getId()).thenReturn(42L);
        when(userRepository.findByEmailIgnoreCase("owner@example.test")).thenReturn(Optional.of(user));
        when(datasetRepository.findActiveOwnedByIdForUpdate(17L, 42L)).thenReturn(Optional.of(dataset));
        when(dataset.getFileName()).thenReturn("sales.csv");
        when(storageService.readRecords(dataset)).thenReturn(List.of(Map.of("value", 1)));
        when(restTemplate.postForEntity(anyString(), any(HttpEntity.class), eq(byte[].class)))
                .thenReturn(ResponseEntity.ok(new byte[]{1, 2, 3}));
        ReportGenerationService service = new ReportGenerationService(
                datasetRepository,
                storageService,
                mock(ReportRepository.class),
                userRepository,
                restTemplate);
        ReflectionTestUtils.setField(service, "mlServiceBaseUrl", "http://ml.test");
        ReflectionTestUtils.setField(service, "internalApiKey", "0123456789abcdef0123456789abcdef");

        ResponseEntity<ByteArrayResource> response = service.generate(17L, "PDF", "owner@example.test");

        assertEquals(HttpStatus.OK, response.getStatusCode());
        var request = org.mockito.ArgumentCaptor.forClass(HttpEntity.class);
        verify(restTemplate).postForEntity(
                eq("http://ml.test/api/ml/reports/generate"),
                request.capture(),
                eq(byte[].class));
        assertEquals(
                "0123456789abcdef0123456789abcdef",
                request.getValue().getHeaders().getFirst("X-Internal-Key"));
    }
}
