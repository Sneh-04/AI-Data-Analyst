package com.aidataanalyst.controller;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.entity.Workspace;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.UserRepository;
import com.aidataanalyst.repository.WorkspaceRepository;
import com.aidataanalyst.service.DatasetStorageService;
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
            storageService.store(storageName, content);
            CsvShape shape = inspect(content);
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
        String[] lines = text.split("\\R");
        if (lines.length == 0 || lines[0].isBlank()) {
            return new CsvShape(0, 0);
        }
        int rows = 0;
        for (int index = 1; index < lines.length; index++) {
            if (!lines[index].isBlank()) {
                rows++;
            }
        }
        return new CsvShape(rows, countColumns(lines[0]));
    }

    private int countColumns(String header) {
        return header.isBlank() ? 0 : header.split(",", -1).length;
    }

    private record CsvShape(int rowCount, int columnCount) {
    }
}
