package com.aidataanalyst.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.DefaultResourceLoader;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.List;
import java.util.Map;

@Service
public class ResearchSummaryService {

    private static final TypeReference<Map<String, Object>> SUMMARY_TYPE = new TypeReference<>() {
    };
    private static final List<String> REQUIRED_FIELDS = List.of(
            "schema_version",
            "source_files",
            "study",
            "coverage",
            "exploratory"
    );
    private static final List<String> DEFAULT_SUMMARY_CANDIDATES = List.of(
            "classpath:research/v4_summary.json",
            "frontend/public/research/v4_summary.json",
            "../frontend/public/research/v4_summary.json",
            "research/v4_summary.json",
            "./research/v4_summary.json"
    );

    private final ObjectMapper objectMapper;
    private final ResourceLoader resourceLoader;
    private final String configuredSummaryPath;
    private final String expectedSha256;
    private volatile String lastResolvedArtifactPath;
    private volatile String lastVerifiedSha256;

    @Autowired
    public ResearchSummaryService(
            ObjectMapper objectMapper,
            @Value("${research.summary.path:}") String summaryPath,
            @Value("${research.summary.expected-sha256:}") String expectedSha256) {
        this(objectMapper, new DefaultResourceLoader(), summaryPath, expectedSha256);
    }

    private ResearchSummaryService(
            ObjectMapper objectMapper,
            ResourceLoader resourceLoader,
            String summaryPath,
            String expectedSha256) {
        this.objectMapper = objectMapper;
        this.resourceLoader = resourceLoader;
        this.configuredSummaryPath = normalizeConfiguredPath(summaryPath);
        this.expectedSha256 = normalizeExpectedChecksum(expectedSha256);
    }

    public Map<String, Object> loadSummary() {
        Resource summaryResource = resolveSummaryResource();
        if (summaryResource == null || !summaryResource.exists() || !summaryResource.isReadable()) {
            throw new ResponseStatusException(
                    HttpStatus.NOT_FOUND,
                    "Research summary artifact is unavailable.");
        }

        final byte[] rawBytes;
        try (InputStream inputStream = summaryResource.getInputStream()) {
            rawBytes = inputStream.readAllBytes();
        } catch (IOException exception) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Unable to read the research summary artifact.",
                    exception);
        }

        final String rawJson = new String(rawBytes, StandardCharsets.UTF_8);
        final Map<String, Object> summary;
        try {
            summary = objectMapper.readValue(rawJson, SUMMARY_TYPE);
        } catch (IOException exception) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Research summary artifact is not valid JSON.",
                    exception);
        }

        validateSummary(summary);

        final String actualSha256 = computeSha256(rawBytes);
        lastResolvedArtifactPath = describeResource(summaryResource);

        if (expectedSha256 != null && !expectedSha256.isBlank() && !expectedSha256.equalsIgnoreCase(actualSha256)) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Research summary checksum mismatch for " + lastResolvedArtifactPath + ": expected "
                            + expectedSha256 + " but computed " + actualSha256);
        }

        lastVerifiedSha256 = actualSha256;
        return summary;
    }

    public String getLastResolvedArtifactPath() {
        return lastResolvedArtifactPath;
    }

    public String getLastVerifiedSha256() {
        return lastVerifiedSha256;
    }

    private void validateSummary(Map<String, Object> summary) {
        if (summary == null || summary.isEmpty()) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Research summary artifact is empty.");
        }

        Object schemaVersion = summary.get("schema_version");
        if (!(schemaVersion instanceof Number number) || number.intValue() != 1) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Unsupported research summary schema version: " + schemaVersion);
        }

        for (String field : REQUIRED_FIELDS) {
            if (!summary.containsKey(field)) {
                throw new ResponseStatusException(
                        HttpStatus.INTERNAL_SERVER_ERROR,
                        "Research summary is missing required field: " + field);
            }
        }

        Object sourceFiles = summary.get("source_files");
        if (!(sourceFiles instanceof Map<?, ?>)) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Research summary source_files field must be an object.");
        }

        Object study = summary.get("study");
        if (!(study instanceof Map<?, ?>)) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Research summary study field must be an object.");
        }

        Object coverage = summary.get("coverage");
        if (!(coverage instanceof java.util.List<?>)) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Research summary coverage field must be a list.");
        }

        Object exploratory = summary.get("exploratory");
        if (!(exploratory instanceof java.util.List<?>)) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Research summary exploratory field must be a list.");
        }
    }

    private String computeSha256(byte[] content) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(content);
            StringBuilder builder = new StringBuilder(digest.length * 2);
            for (byte value : digest) {
                builder.append(String.format("%02x", value));
            }
            return builder.toString();
        } catch (NoSuchAlgorithmException exception) {
            throw new ResponseStatusException(
                    HttpStatus.INTERNAL_SERVER_ERROR,
                    "Unable to compute the research summary checksum.",
                    exception);
        }
    }

    private Resource resolveSummaryResource() {
        if (configuredSummaryPath != null && !configuredSummaryPath.isBlank()) {
            Resource configured = resolveResource(configuredSummaryPath);
            if (configured != null && configured.exists() && configured.isReadable()) {
                return configured;
            }
        }

        for (String candidate : DEFAULT_SUMMARY_CANDIDATES) {
            Resource resource = resolveResource(candidate);
            if (resource != null && resource.exists() && resource.isReadable()) {
                return resource;
            }
        }
        return null;
    }

    private Resource resolveResource(String value) {
        String normalized = value == null ? "" : value.trim();
        if (normalized.isEmpty()) {
            return null;
        }

        if (normalized.startsWith("classpath:")) {
            return resourceLoader.getResource(normalized);
        }
        if (normalized.startsWith("file:")) {
            return resourceLoader.getResource(normalized);
        }

        Path filePath = normalizePath(normalized);
        if (filePath != null && java.nio.file.Files.isRegularFile(filePath)) {
            return new FileSystemResource(filePath);
        }

        Resource classpathResource = resourceLoader.getResource("classpath:" + normalized);
        if (classpathResource.exists() && classpathResource.isReadable()) {
            return classpathResource;
        }

        return resourceLoader.getResource(normalized);
    }

    private String describeResource(Resource resource) {
        try {
            return resource.getURL().toString();
        } catch (IOException exception) {
            String fileName = resource.getFilename();
            return fileName == null ? "classpath resource" : fileName;
        }
    }

    private Path normalizePath(String value) {
        String normalized = value == null ? "" : value.trim();
        if (normalized.isEmpty()) {
            return null;
        }
        return Path.of(normalized);
    }

    private String normalizeConfiguredPath(String value) {
        if (value == null) {
            return null;
        }
        String normalized = value.trim();
        return normalized.isEmpty() ? null : normalized;
    }

    private String normalizeExpectedChecksum(String value) {
        if (value == null) {
            return null;
        }
        String normalized = value.trim();
        return normalized.isEmpty() ? null : normalized;
    }
}
