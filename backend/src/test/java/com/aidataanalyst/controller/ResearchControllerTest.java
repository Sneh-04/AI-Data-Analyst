package com.aidataanalyst.controller;

import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.UserRepository;
import com.aidataanalyst.security.JwtService;
import com.aidataanalyst.service.ResearchSummaryService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = {
        "jwt.secret=researchtestsecret1234567890abcdef",
        "jwt.expiration-ms=60000",
        "spring.datasource.url=jdbc:h2:mem:research-api;MODE=PostgreSQL;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE",
        "spring.datasource.driver-class-name=org.h2.Driver",
        "spring.datasource.username=sa",
        "spring.datasource.password=",
        "spring.jpa.hibernate.ddl-auto=create-drop",
        "spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.H2Dialect",
        "spring.flyway.enabled=false",
        "ml.service.base-url=http://localhost:8000",
        "INTERNAL_API_KEY=test-internal-api-key-0123456789abcdef",
        "storage.local-path=${java.io.tmpdir}/research-api-test"
})
class ResearchControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private ObjectMapper objectMapper;

    @org.springframework.boot.test.mock.mockito.MockBean
    private ResearchSummaryService researchSummaryService;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void authenticatedRequestReceivesResearchSummary() throws Exception {
        String summaryJson = validSummaryJson();
        Map<String, Object> summary = objectMapper.readValue(summaryJson, Map.class);
        User user = userRepository.save(new User("user@example.com", "hashed-password", "Research User"));
        String token = jwtService.generateToken(user.getEmail());

        org.mockito.Mockito.when(researchSummaryService.loadSummary()).thenReturn(summary);
        org.mockito.Mockito.when(researchSummaryService.getLastResolvedArtifactPath()).thenReturn("/tmp/approved-research.json");
        org.mockito.Mockito.when(researchSummaryService.getLastVerifiedSha256()).thenReturn("abc123");

        mockMvc.perform(get("/api/research/v4/summary")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(content().json(summaryJson))
                .andExpect(header().string("X-Research-Artifact-Version", "v4"))
                .andExpect(header().string("X-Research-Artifact-Path", "/tmp/approved-research.json"))
                .andExpect(header().string("X-Research-Artifact-Sha256", "abc123"));
    }

    @Test
    void unauthenticatedRequestIsRejected() throws Exception {
        mockMvc.perform(get("/api/research/v4/summary"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void serviceRejectsChecksumMismatch(@TempDir Path tempDir) throws IOException {
        Path artifact = tempDir.resolve("summary.json");
        Files.writeString(artifact, validSummaryJson(), StandardCharsets.UTF_8);

        ResearchSummaryService service = new ResearchSummaryService(new ObjectMapper(), artifact.toString(), "expected-sha256");

        ResponseStatusException exception = assertThrows(ResponseStatusException.class, service::loadSummary);
        assertEquals(500, exception.getStatusCode().value());
    }

    @Test
    void serviceLoadsSummaryWhenChecksumConfigurationIsBlank(@TempDir Path tempDir) throws IOException {
        Path artifact = tempDir.resolve("summary.json");
        String originalContents = validSummaryJson();
        Files.writeString(artifact, originalContents, StandardCharsets.UTF_8);

        ResearchSummaryService service = new ResearchSummaryService(new ObjectMapper(), artifact.toString(), "");
        Map<String, Object> loaded = service.loadSummary();

        assertEquals(1, loaded.get("schema_version"));
        assertEquals(sha256Hex(artifact), service.getLastVerifiedSha256());
    }

    @Test
    void serviceRejectsUnsupportedSchemaVersion(@TempDir Path tempDir) throws IOException {
        Path artifact = tempDir.resolve("summary.json");
        Files.writeString(artifact, invalidVersionSummaryJson(), StandardCharsets.UTF_8);

        String expectedHash = sha256Hex(artifact);
        ResearchSummaryService service = new ResearchSummaryService(new ObjectMapper(), artifact.toString(), expectedHash);

        ResponseStatusException exception = assertThrows(ResponseStatusException.class, service::loadSummary);
        assertEquals(500, exception.getStatusCode().value());
    }

    @Test
    void serviceRejectsMalformedJson(@TempDir Path tempDir) throws IOException {
        Path artifact = tempDir.resolve("summary.json");
        Files.writeString(artifact, "{not-json}", StandardCharsets.UTF_8);

        ResearchSummaryService service = new ResearchSummaryService(new ObjectMapper(), artifact.toString(), "1234");

        ResponseStatusException exception = assertThrows(ResponseStatusException.class, service::loadSummary);
        assertEquals(500, exception.getStatusCode().value());
    }

    @Test
    void serviceLoadsAndVerifiesApprovedSummary(@TempDir Path tempDir) throws IOException {
        Path artifact = tempDir.resolve("summary.json");
        String originalContents = validSummaryJson();
        Files.writeString(artifact, originalContents, StandardCharsets.UTF_8);
        String expectedHash = sha256Hex(artifact);

        ResearchSummaryService service = new ResearchSummaryService(new ObjectMapper(), artifact.toString(), expectedHash);
        Map<String, Object> loaded = service.loadSummary();

        assertEquals(1, loaded.get("schema_version"));
        assertEquals(expectedHash, service.getLastVerifiedSha256());
        assertEquals(originalContents, Files.readString(artifact, StandardCharsets.UTF_8));
    }

    private static String validSummaryJson() {
        return "{"
                + "\"schema_version\":1,"
                + "\"source_files\":{\"primary\":\"experiments/results/rubin_coverage_full_v4/headline_coverage.csv\"},"
                + "\"study\":{\"design\":{\"dataset_count\":10}},"
                + "\"coverage\":[{\"method\":\"knn\",\"coverage\":0.85}],"
                + "\"exploratory\":[{\"label\":\"exploratory\"}],"
                + "\"tags\":[\"rubin-v4\"],"
                + "\"caveats\":[\"test caveat\"]"
                + "}";
    }

    private static String invalidVersionSummaryJson() {
        return "{"
                + "\"schema_version\":2,"
                + "\"source_files\":{\"primary\":\"experiments/results/rubin_coverage_full_v4/headline_coverage.csv\"},"
                + "\"study\":{\"design\":{\"dataset_count\":10}},"
                + "\"coverage\":[],"
                + "\"exploratory\":[]"
                + "}";
    }

    private static String sha256Hex(Path path) throws IOException {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(path));
            StringBuilder builder = new StringBuilder(digest.length * 2);
            for (byte value : digest) {
                builder.append(String.format("%02x", value));
            }
            return builder.toString();
        } catch (Exception exception) {
            throw new IOException("Unable to hash the fixture.", exception);
        }
    }
}
