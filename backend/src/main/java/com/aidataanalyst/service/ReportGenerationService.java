package com.aidataanalyst.service;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.Report;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.ReportRepository;
import com.aidataanalyst.repository.UserRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.util.Map;
import java.util.UUID;

import static org.springframework.http.HttpStatus.BAD_REQUEST;
import static org.springframework.http.HttpStatus.NOT_FOUND;
import static org.springframework.http.HttpStatus.UNAUTHORIZED;

@Service
public class ReportGenerationService {

    private final DatasetRepository datasetRepository;
    private final DatasetStorageService storageService;
    private final ReportRepository reportRepository;
    private final UserRepository userRepository;
    private final RestTemplate restTemplate;

    @Value("${ml.service.base-url:http://localhost:8000}")
    private String mlServiceBaseUrl;

    public ReportGenerationService(DatasetRepository datasetRepository, DatasetStorageService storageService,
                                   ReportRepository reportRepository, UserRepository userRepository,
                                   RestTemplate restTemplate) {
        this.datasetRepository = datasetRepository;
        this.storageService = storageService;
        this.reportRepository = reportRepository;
        this.userRepository = userRepository;
        this.restTemplate = restTemplate;
    }

    @Transactional
    public ResponseEntity<ByteArrayResource> generate(Long datasetId, String requestedFormat, String email) {
        String format = requestedFormat == null ? "PDF" : requestedFormat.toUpperCase();
        if (!format.equals("PDF") && !format.equals("XLSX")) {
            throw new ResponseStatusException(BAD_REQUEST, "Format must be PDF or XLSX");
        }
        Dataset dataset = datasetRepository.findById(datasetId)
                .orElseThrow(() -> new ResponseStatusException(NOT_FOUND, "Dataset not found"));
        User user = userRepository.findByEmailIgnoreCase(email)
                .orElseThrow(() -> new ResponseStatusException(UNAUTHORIZED, "User is unavailable"));

        Map<String, Object> payload = Map.of(
                "records", storageService.readRecords(dataset),
                "format", format,
                "dataset_name", dataset.getFileName());
        HttpHeaders requestHeaders = new HttpHeaders();
        requestHeaders.setContentType(MediaType.APPLICATION_JSON);
        ResponseEntity<byte[]> mlResponse = restTemplate.postForEntity(
                mlServiceBaseUrl + "/api/ml/reports/generate",
                new HttpEntity<>(payload, requestHeaders), byte[].class);
        byte[] content = mlResponse.getBody();
        if (content == null || content.length == 0) {
            throw new ResponseStatusException(NOT_FOUND, "Report service returned no file");
        }

        String extension = format.equals("PDF") ? "pdf" : "xlsx";
        String storagePath = "reports/" + UUID.randomUUID() + "." + extension;
        try {
            storageService.store(storagePath, content);
        } catch (IOException exception) {
            throw new ResponseStatusException(org.springframework.http.HttpStatus.INTERNAL_SERVER_ERROR,
                    "Unable to store report", exception);
        }
        reportRepository.save(new Report(datasetId, format, storagePath, user.getId()));

        MediaType mediaType = format.equals("PDF") ? MediaType.APPLICATION_PDF
                : MediaType.parseMediaType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
        String downloadName = "dataset-" + datasetId + "-report." + extension;
        HttpHeaders responseHeaders = new HttpHeaders();
        responseHeaders.setContentType(mediaType);
        responseHeaders.setContentLength(content.length);
        responseHeaders.setContentDisposition(ContentDisposition.attachment().filename(downloadName).build());
        return new ResponseEntity<>(new ByteArrayResource(content), responseHeaders, org.springframework.http.HttpStatus.OK);
    }
}
