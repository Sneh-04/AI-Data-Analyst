package com.aidataanalyst.controller;

import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.UserRepository;
import com.aidataanalyst.security.JwtService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.aidataanalyst.Application;
import com.sun.net.httpserver.HttpServer;
import org.flywaydb.core.Flyway;
import org.flywaydb.core.api.MigrationVersion;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.WebApplicationType;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class DatasetDeletionPostgresIntegrationTest {

    private static final String JWT_SECRET = "integration-jwt-secret-0123456789abcdef";
    private static final String INTERNAL_API_KEY = "integration-ml-key-0123456789abcdef";
    private static final Path STORAGE_ROOT = Path.of(
            System.getProperty("java.io.tmpdir"), "dataset-deletion-it-" + UUID.randomUUID());

    private static final AtomicBoolean mlServiceAuthenticated = new AtomicBoolean();
    private static final AtomicReference<String> chatRequestBody = new AtomicReference<>();
    private static PostgreSQLContainer<?> postgresContainer;
    private static HttpServer mlService;
    private static String datasourceUrl;
    private static String datasourceUsername;
    private static String datasourcePassword;

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        String jdbcUrl = System.getenv("DELETION_TEST_JDBC_URL");
        String username = System.getenv("DELETION_TEST_DB_USERNAME");
        String password = System.getenv("DELETION_TEST_DB_PASSWORD");
        if (jdbcUrl == null || username == null || password == null) {
            postgresContainer = new PostgreSQLContainer<>(
                    DockerImageName.parse("pgvector/pgvector:pg16").asCompatibleSubstituteFor("postgres"));
            postgresContainer.start();
            jdbcUrl = postgresContainer.getJdbcUrl();
            username = postgresContainer.getUsername();
            password = postgresContainer.getPassword();
        }
        datasourceUrl = jdbcUrl;
        datasourceUsername = username;
        datasourcePassword = password;
        try {
            mlService = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            mlService.createContext("/api/ml/", exchange -> {
                if (!INTERNAL_API_KEY.equals(exchange.getRequestHeaders().getFirst("X-Internal-Key"))) {
                    exchange.sendResponseHeaders(401, -1);
                    exchange.close();
                    return;
                }
                mlServiceAuthenticated.set(true);
                String path = exchange.getRequestURI().getPath();
                byte[] requestBody = exchange.getRequestBody().readAllBytes();
                if ("/api/ml/chat/ask".equals(path)) {
                    chatRequestBody.set(new String(requestBody, StandardCharsets.UTF_8));
                }
                byte[] response = switch (path) {
                    case "/api/ml/cleaning/clean" -> """
                            {"cleaned_records":[{"amount":10,"region":"west"}],"summary":{"rows":1}}
                            """.getBytes(StandardCharsets.UTF_8);
                    case "/api/ml/health/score" -> """
                            {"score":95,"grade":"A"}
                            """.getBytes(StandardCharsets.UTF_8);
                    case "/api/ml/forecasting/run" -> """
                            {"forecast":[{"month":"2026-01","amount":12}],"model_used":"test"}
                            """.getBytes(StandardCharsets.UTF_8);
                    case "/api/ml/chat/ask" -> """
                            {"answer":"Synthetic integration-test summary"}
                            """.getBytes(StandardCharsets.UTF_8);
                    case "/api/ml/reports/generate" ->
                            "%PDF-1.4 integration fixture".getBytes(StandardCharsets.UTF_8);
                    default -> new byte[0];
                };
                exchange.getResponseHeaders().set(
                        "Content-Type", path.endsWith("/reports/generate") ? "application/pdf" : "application/json");
                exchange.sendResponseHeaders(200, response.length);
                try (var output = exchange.getResponseBody()) {
                    output.write(response);
                }
            });
            mlService.start();
        } catch (IOException exception) {
            throw new IllegalStateException("Unable to start local ML-service test fixture", exception);
        }
        String mlServiceUrl = "http://127.0.0.1:" + mlService.getAddress().getPort();
        registry.add("spring.datasource.url", () -> datasourceUrl);
        registry.add("spring.datasource.username", () -> datasourceUsername);
        registry.add("spring.datasource.password", () -> datasourcePassword);
        registry.add("spring.jpa.hibernate.ddl-auto", () -> "validate");
        registry.add("spring.flyway.enabled", () -> "true");
        registry.add("spring.flyway.baseline-on-migrate", () -> "false");
        registry.add("jwt.secret", () -> JWT_SECRET);
        registry.add("INTERNAL_API_KEY", () -> INTERNAL_API_KEY);
        registry.add("ml.service.base-url", () -> mlServiceUrl);
        registry.add("storage.local-path", () -> STORAGE_ROOT.toString());
    }

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private ObjectMapper objectMapper;

    private User owner;
    private User otherUser;

    @BeforeEach
    void createUsers() {
        owner = userRepository.save(new User("owner-" + UUID.randomUUID() + "@test.invalid", "hash", "Owner"));
        otherUser = userRepository.save(
                new User("other-" + UUID.randomUUID() + "@test.invalid", "hash", "Other"));
    }

    @AfterAll
    static void removeTemporaryStorage() throws IOException {
        if (mlService != null) {
            mlService.stop(0);
        }
        if (postgresContainer != null) {
            postgresContainer.stop();
        }
        if (Files.exists(STORAGE_ROOT)) {
            try (var paths = Files.walk(STORAGE_ROOT)) {
                for (Path path : paths.sorted(Comparator.reverseOrder()).toList()) {
                    Files.deleteIfExists(path);
                }
            }
        }
    }

    @Test
    void appliesV1ThroughV3ThenDeletesAllDatasetRowsAndFilesAndBlocksOtherUsers() throws Exception {
        UploadedDataset uploaded = generateRelatedArtifacts(uploadDataset(owner), owner.getId());

        assertEquals(1, count("dataset_health_scores", uploaded.datasetId()));
        assertEquals(1, count("dataset_versions", uploaded.datasetId()));
        assertEquals(1, count("dashboards", uploaded.datasetId()));
        assertEquals(1, count("forecasts", uploaded.datasetId()));
        assertEquals(1, count("reports", uploaded.datasetId()));
        assertEquals(1, count("chat_sessions", uploaded.datasetId()));
        assertEquals(2, jdbcTemplate.queryForObject(
                "select count(*) from chat_messages where session_id = ?", Integer.class, uploaded.chatSessionId()));
        assertEquals(1, jdbcTemplate.queryForObject(
                "select count(*) from datasets where id = ? and schema_embedding_openai is not null",
                Integer.class, uploaded.datasetId()));
        assertEquals(1, jdbcTemplate.queryForObject(
                "select count(*) from datasets where id = ? and schema_embedding_ollama is not null",
                Integer.class, uploaded.datasetId()));
        assertTrue(mlServiceAuthenticated.get());
        assertEquals(uploaded.datasetId(),
                objectMapper.readTree(chatRequestBody.get()).get("dataset_id").asLong());

        mockMvc.perform(get("/api/datasets/{id}/records", uploaded.datasetId())
                        .header("Authorization", bearer(owner)))
                .andExpect(status().isOk());

        mockMvc.perform(get("/api/datasets/{id}/records", uploaded.datasetId())
                        .header("Authorization", bearer(otherUser)))
                .andExpect(status().isNotFound());
        mockMvc.perform(get("/api/datasets/{id}/versions", uploaded.datasetId())
                        .header("Authorization", bearer(owner)))
                .andExpect(status().isOk());
        mockMvc.perform(delete("/api/datasets/{id}", uploaded.datasetId())
                        .header("Authorization", bearer(otherUser)))
                .andExpect(status().isNotFound());
        mockMvc.perform(get("/api/datasets/{id}/versions", uploaded.datasetId())
                        .header("Authorization", bearer(otherUser)))
                .andExpect(status().isNotFound());
        mockMvc.perform(get("/api/datasets/{id}/health-score/history", uploaded.datasetId())
                        .header("Authorization", bearer(otherUser)))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/clean", uploaded.datasetId())
                        .header("Authorization", bearer(otherUser))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/health-score", uploaded.datasetId())
                        .header("Authorization", bearer(otherUser))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/forecast", uploaded.datasetId())
                        .header("Authorization", bearer(otherUser))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/chat", uploaded.datasetId())
                        .header("Authorization", bearer(otherUser))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"dataset_id\":999,\"question\":\"read\"}"))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/reports", uploaded.datasetId())
                        .header("Authorization", bearer(otherUser))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"format\":\"PDF\"}"))
                .andExpect(status().isNotFound());
        assertEquals(1, count("datasets", uploaded.datasetId()));
        assertTrue(Files.exists(uploaded.sourceFile()));
        long previousDeletionJobId = latestDeletionJobId();

        mockMvc.perform(delete("/api/datasets/{id}", uploaded.datasetId())
                        .header("Authorization", bearer(owner)))
                .andExpect(status().isNoContent());

        assertEquals(0, count("datasets", uploaded.datasetId()));
        assertEquals(0, count("dataset_health_scores", uploaded.datasetId()));
        assertEquals(0, count("dataset_versions", uploaded.datasetId()));
        assertEquals(0, count("dashboards", uploaded.datasetId()));
        assertEquals(0, count("forecasts", uploaded.datasetId()));
        assertEquals(0, count("reports", uploaded.datasetId()));
        assertEquals(0, count("chat_sessions", uploaded.datasetId()));
        assertEquals(0, jdbcTemplate.queryForObject(
                "select count(*) from chat_messages where session_id = ?", Integer.class, uploaded.chatSessionId()));
        assertFalse(Files.exists(uploaded.sourceFile()));
        assertFalse(Files.exists(uploaded.versionFile()));
        assertFalse(Files.exists(uploaded.reportFile()));
        long deletionJobId = jdbcTemplate.queryForObject(
                "select max(id) from dataset_deletion_jobs where id > ?", Long.class, previousDeletionJobId);
        assertEquals("COMPLETED", jdbcTemplate.queryForObject(
                "select status from dataset_deletion_jobs where id = ?", String.class, deletionJobId));
        assertEquals(1, jdbcTemplate.queryForObject("""
                select count(*) from dataset_deletion_jobs
                where id = ? and dataset_id is null and requested_by_id is null and completed_at is not null
                """, Integer.class, deletionJobId));

        mockMvc.perform(get("/api/datasets/{id}/records", uploaded.datasetId())
                        .header("Authorization", bearer(owner)))
                .andExpect(status().isNotFound());
        mockMvc.perform(get("/api/datasets/{id}/versions", uploaded.datasetId())
                        .header("Authorization", bearer(owner)))
                .andExpect(status().isNotFound());
        mockMvc.perform(get("/api/datasets/{id}/health-score/history", uploaded.datasetId())
                        .header("Authorization", bearer(owner)))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/clean", uploaded.datasetId())
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/health-score", uploaded.datasetId())
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/forecast", uploaded.datasetId())
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"date_column\":\"month\",\"value_column\":\"amount\"}"))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/chat", uploaded.datasetId())
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"dataset_id\":999,\"question\":\"read\"}"))
                .andExpect(status().isNotFound());
        mockMvc.perform(post("/api/datasets/{id}/reports", uploaded.datasetId())
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"format\":\"PDF\"}"))
                .andExpect(status().isNotFound());
        mockMvc.perform(delete("/api/datasets/{id}", uploaded.datasetId())
                        .header("Authorization", bearer(owner)))
                .andExpect(status().isNotFound());
    }

    @Test
    void v3RedactsCompletedJobsFromPopulatedV2WithoutChangingRetryableJobs() {
        String schema = "deletion_upgrade_" + UUID.randomUUID().toString().replace("-", "");
        jdbcTemplate.execute("create schema " + schema);
        try {
            Flyway.configure()
                    .dataSource(datasourceUrl, datasourceUsername, datasourcePassword)
                    .schemas(schema)
                    .defaultSchema(schema)
                    .locations("classpath:db/migration")
                    .target(MigrationVersion.fromVersion("2"))
                    .load()
                    .migrate();

            String users = schema + ".users";
            String workspaces = schema + ".workspaces";
            String datasets = schema + ".datasets";
            String jobs = schema + ".dataset_deletion_jobs";
            Long userId = jdbcTemplate.queryForObject(
                    "insert into " + users + " (email, password_hash) values (?, ?) returning id",
                    Long.class, "migration-owner-" + UUID.randomUUID() + "@test.invalid", "hash");
            Long workspaceId = jdbcTemplate.queryForObject(
                    "insert into " + workspaces + " (name, owner_id) values (?, ?) returning id",
                    Long.class, "migration-workspace", userId);
            Long pendingDatasetId = jdbcTemplate.queryForObject(
                    "insert into " + datasets
                            + " (workspace_id, uploaded_by, file_name, storage_path, deletion_status)"
                            + " values (?, ?, ?, ?, 'DELETING') returning id",
                    Long.class, workspaceId, userId, "pending.csv", "pending.csv");
            Long completedJobId = jdbcTemplate.queryForObject(
                    "insert into " + jobs
                            + " (dataset_id, requested_by_id, status, completed_at)"
                            + " values (?, ?, 'COMPLETED', now()) returning id",
                    Long.class, 900001L, 910001L);
            Long pendingJobId = jdbcTemplate.queryForObject(
                    "insert into " + jobs
                            + " (dataset_id, requested_by_id, status)"
                            + " values (?, ?, 'FAILED') returning id",
                    Long.class, pendingDatasetId, userId);

            Flyway.configure()
                    .dataSource(datasourceUrl, datasourceUsername, datasourcePassword)
                    .schemas(schema)
                    .defaultSchema(schema)
                    .locations("classpath:db/migration")
                    .load()
                    .migrate();

            assertEquals(1, jdbcTemplate.queryForObject("""
                    select count(*) from %s
                    where id = ? and status = 'COMPLETED' and dataset_id is null
                        and requested_by_id is null and completed_at is not null
                    """.formatted(jobs), Integer.class, completedJobId));
            assertEquals(1, jdbcTemplate.queryForObject("""
                    select count(*) from %s
                    where id = ? and status = 'FAILED' and dataset_id = ?
                        and requested_by_id = ? and completed_at is null
                    """.formatted(jobs), Integer.class, pendingJobId, pendingDatasetId, userId));
            assertEquals(1, jdbcTemplate.queryForObject(
                    "select count(*) from " + datasets + " where id = ? and deletion_status = 'DELETING'",
                    Integer.class, pendingDatasetId));
        } finally {
            jdbcTemplate.execute("drop schema if exists " + schema + " cascade");
        }
    }

    @Test
    void persistedDeletionFailureCanBeRetriedAfterTheStorageErrorIsResolved() throws Exception {
        UploadedDataset uploaded = uploadDataset(owner);
        Files.delete(uploaded.sourceFile());
        Files.createDirectory(uploaded.sourceFile());
        Path obstruction = uploaded.sourceFile().resolve("not-empty");
        Files.writeString(obstruction, "retry fixture");

        mockMvc.perform(delete("/api/datasets/{id}", uploaded.datasetId())
                        .header("Authorization", bearer(owner)))
                .andExpect(status().isInternalServerError());

        assertEquals("DELETING", jdbcTemplate.queryForObject(
                "select deletion_status from datasets where id = ?", String.class, uploaded.datasetId()));
        assertEquals("FAILED", jdbcTemplate.queryForObject(
                "select status from dataset_deletion_jobs where dataset_id = ?", String.class, uploaded.datasetId()));
        assertEquals(1, jdbcTemplate.queryForObject("""
                select count(*) from dataset_deletion_jobs
                where dataset_id = ? and requested_by_id = ? and completed_at is null
                """, Integer.class, uploaded.datasetId(), owner.getId()));
        Long deletionJobId = jdbcTemplate.queryForObject(
                "select id from dataset_deletion_jobs where dataset_id = ?", Long.class, uploaded.datasetId());
        mockMvc.perform(get("/api/datasets/{id}/records", uploaded.datasetId())
                        .header("Authorization", bearer(owner)))
                .andExpect(status().isNotFound());

        Files.delete(obstruction);
        try (ConfigurableApplicationContext restartedApplication = new SpringApplicationBuilder(Application.class)
                .web(WebApplicationType.NONE)
                .run(
                        "--spring.datasource.url=" + datasourceUrl,
                        "--spring.datasource.username=" + datasourceUsername,
                        "--spring.datasource.password=" + datasourcePassword,
                        "--spring.jpa.hibernate.ddl-auto=validate",
                        "--spring.flyway.baseline-on-migrate=false",
                        "--jwt.secret=" + JWT_SECRET,
                        "--INTERNAL_API_KEY=" + INTERNAL_API_KEY,
                        "--ml.service.base-url=http://127.0.0.1:" + mlService.getAddress().getPort(),
                        "--storage.local-path=" + STORAGE_ROOT)) {
            restartedApplication.getBean(com.aidataanalyst.service.DatasetDeletionService.class)
                    .delete(uploaded.datasetId(), owner.getEmail());
        }

        assertEquals(0, count("datasets", uploaded.datasetId()));
        assertEquals("COMPLETED", jdbcTemplate.queryForObject(
                "select status from dataset_deletion_jobs where id = ?", String.class, deletionJobId));
        assertEquals(1, jdbcTemplate.queryForObject("""
                select count(*) from dataset_deletion_jobs
                where id = ? and dataset_id is null and requested_by_id is null and completed_at is not null
                """, Integer.class, deletionJobId));
    }

    private UploadedDataset uploadDataset(User user) throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "sales.csv", "text/csv", "amount,region\n10,west\n".getBytes());
        MvcResult result = mockMvc.perform(multipart("/api/datasets/upload")
                        .file(file)
                        .header("Authorization", bearer(user)))
                .andExpect(status().isCreated())
                .andReturn();
        JsonNode response = objectMapper.readTree(result.getResponse().getContentAsByteArray());
        long datasetId = response.get("datasetId").asLong();
        String storagePath = jdbcTemplate.queryForObject(
                "select storage_path from datasets where id = ?", String.class, datasetId);
        Path sourceFile = STORAGE_ROOT.resolve(storagePath);
        return new UploadedDataset(datasetId, sourceFile, null, null, null);
    }

    private UploadedDataset generateRelatedArtifacts(UploadedDataset uploaded, long userId) throws Exception {
        long datasetId = uploaded.datasetId();
        mockMvc.perform(post("/api/datasets/{id}/clean", datasetId)
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"records\":[{\"amount\":10,\"region\":\"west\"}]}"))
                .andExpect(status().isOk());
        mockMvc.perform(post("/api/datasets/{id}/health-score", datasetId)
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{}"))
                .andExpect(status().isOk());
        mockMvc.perform(post("/api/datasets/{id}/forecast", datasetId)
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"date_column\":\"month\",\"value_column\":\"amount\"}"))
                .andExpect(status().isOk());
        mockMvc.perform(post("/api/datasets/{id}/chat", datasetId)
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"question\":\"Summarize\",\"dataset_id\":999}"))
                .andExpect(status().isOk());
        mockMvc.perform(post("/api/datasets/{id}/reports", datasetId)
                        .header("Authorization", bearer(owner))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"format\":\"PDF\"}"))
                .andExpect(status().isOk());

        jdbcTemplate.update("""
                insert into dashboards (dataset_id, created_by, title, layout_json)
                values (?, ?, 'Overview', '{}'::jsonb)
                """, datasetId, userId);

        String versionPath = jdbcTemplate.queryForObject(
                "select storage_path from dataset_versions where dataset_id = ?", String.class, datasetId);
        String reportPath = jdbcTemplate.queryForObject(
                "select storage_path from reports where dataset_id = ?", String.class, datasetId);
        long chatSessionId = jdbcTemplate.queryForObject(
                "select id from chat_sessions where dataset_id = ? order by id desc limit 1", Long.class, datasetId);
        String embedding = "[" + "0,".repeat(1535) + "0]";
        jdbcTemplate.update(
                "update datasets set schema_embedding_openai = ?::vector where id = ?", embedding, datasetId);
        String ollamaEmbedding = "[" + "0,".repeat(767) + "0]";
        jdbcTemplate.update(
                "update datasets set schema_embedding_ollama = ?::vector where id = ?", ollamaEmbedding, datasetId);

        return new UploadedDataset(
                datasetId,
                uploaded.sourceFile(),
                STORAGE_ROOT.resolve(versionPath),
                STORAGE_ROOT.resolve(reportPath),
                chatSessionId);
    }

    private int count(String table, long datasetId) {
        String idColumn = "datasets".equals(table) ? "id" : "dataset_id";
        return jdbcTemplate.queryForObject(
                "select count(*) from " + table + " where " + idColumn + " = ?", Integer.class, datasetId);
    }

    private long latestDeletionJobId() {
        return jdbcTemplate.queryForObject(
                "select coalesce(max(id), 0) from dataset_deletion_jobs", Long.class);
    }

    private String bearer(User user) {
        return "Bearer " + jwtService.generateToken(user.getEmail());
    }

    private record UploadedDataset(
            long datasetId, Path sourceFile, Path versionFile, Path reportFile, Long chatSessionId) {
    }
}
