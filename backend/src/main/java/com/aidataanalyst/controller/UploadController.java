package com.aidataanalyst.controller;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.entity.Workspace;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.UserRepository;
import com.aidataanalyst.repository.WorkspaceRepository;
import com.aidataanalyst.service.DatasetStorageService;
import com.aidataanalyst.service.CsvParser;
import jakarta.validation.constraints.NotNull;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/datasets")
public class UploadController {

    private final DatasetRepository datasetRepository;
    private final DatasetStorageService storageService;
    private final UserRepository userRepository;
    private final WorkspaceRepository workspaceRepository;

    public UploadController(DatasetRepository datasetRepository, DatasetStorageService storageService,
                            UserRepository userRepository, WorkspaceRepository workspaceRepository) {
        this.datasetRepository = datasetRepository;
        this.storageService = storageService;
        this.userRepository = userRepository;
        this.workspaceRepository = workspaceRepository;
    }

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> upload(
            @RequestPart("file") @NotNull MultipartFile file,
            Authentication authentication) {
        if (file.isEmpty() || file.getOriginalFilename() == null) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "A CSV file is required");
        }
        if (!file.getOriginalFilename().toLowerCase().endsWith(".csv")) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Only CSV files are supported");
        }

        User user = userRepository.findByEmailIgnoreCase(authentication.getName())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "User is unavailable"));
        Workspace workspace = workspaceRepository.findFirstByOwnerIdOrderByIdAsc(user.getId())
                .orElseGet(() -> workspaceRepository.save(new Workspace("My Workspace", user.getId())));
        String storageName = UUID.randomUUID() + ".csv";
        try {
            byte[] content = file.getBytes();
            CsvShape shape;
            try {
                shape = inspect(content);
            } catch (IllegalArgumentException exception) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST, exception.getMessage(), exception);
            }
            storageService.store(storageName, content);
            Dataset dataset = datasetRepository.save(new Dataset(
                    workspace.getId(), user.getId(), file.getOriginalFilename(), storageName,
                    shape.rowCount(), shape.columnCount()));
            return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                    "datasetId", dataset.getId(),
                    "fileName", dataset.getFileName(),
                    "rowCount", dataset.getRowCount(),
                    "columnCount", dataset.getColumnCount()));
        } catch (IOException exception) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Unable to store dataset", exception);
        }
    }

    private CsvShape inspect(byte[] content) {
        String text = new String(content, java.nio.charset.StandardCharsets.UTF_8);
        List<List<String>> rows = CsvParser.parseRows(text);
        CsvParser.validateRowWidths(rows);
        if (rows.isEmpty() || rows.get(0).isEmpty() || rows.get(0).get(0).isBlank()) {
            return new CsvShape(0, 0);
        }
        return new CsvShape(rows.size() - 1, rows.get(0).size());
    }

    private record CsvShape(int rowCount, int columnCount) {
    }
}
