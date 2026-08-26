package com.aidataanalyst.service;

import com.aidataanalyst.entity.Dataset;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class DatasetStorageService {

    private final Path storageRoot;

    public DatasetStorageService(@Value("${storage.local-path}") String storagePath) {
        this.storageRoot = Path.of(storagePath).toAbsolutePath().normalize();
    }

    public Path store(String fileName, byte[] content) throws IOException {
        Files.createDirectories(storageRoot);
        Path target = storageRoot.resolve(fileName).normalize();
        if (!target.startsWith(storageRoot)) {
            throw new IOException("Invalid storage path");
        }
        Files.write(target, content);
        return target;
    }

    public Path writeRecords(String fileName, List<Map<String, Object>> records) throws IOException {
        List<String> headers = records.isEmpty() ? List.of() : new ArrayList<>(records.get(0).keySet());
        StringBuilder csv = new StringBuilder();
        csv.append(headers.stream().map(this::escapeCsv).collect(java.util.stream.Collectors.joining(","))).append('\n');
        for (Map<String, Object> record : records) {
            csv.append(headers.stream()
                    .map(header -> escapeCsv(record.get(header)))
                    .collect(java.util.stream.Collectors.joining(","))).append('\n');
        }
        return store(fileName, csv.toString().getBytes(StandardCharsets.UTF_8));
    }

    public List<Map<String, Object>> readRecords(Dataset dataset) {
        return readRecordsFromPath(dataset.getStoragePath());
    }

    public List<Map<String, Object>> readRecordsFromPath(String storagePath) {
        Path file = storageRoot.resolve(storagePath).normalize();
        if (!file.startsWith(storageRoot)) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Invalid dataset storage path");
        }
        try {
            List<String> lines = Files.readAllLines(file, StandardCharsets.UTF_8);
            if (lines.isEmpty() || lines.get(0).isBlank()) {
                return List.of();
            }
            List<String> headers = parseLine(lines.get(0));
            List<Map<String, Object>> records = new ArrayList<>();
            for (String line : lines.subList(1, lines.size())) {
                if (line.isBlank()) {
                    continue;
                }
                List<String> values = parseLine(line);
                Map<String, Object> record = new LinkedHashMap<>();
                for (int index = 0; index < headers.size(); index++) {
                    String value = index < values.size() ? values.get(index).trim() : "";
                    record.put(headers.get(index), parseValue(value));
                }
                records.add(record);
            }
            return records;
        } catch (IOException exception) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset file is unavailable", exception);
        }
    }

    private String escapeCsv(Object value) {
        String text = value == null ? "" : String.valueOf(value);
        return '"' + text.replace("\"", "\"\"") + '"';
    }

    private List<String> parseLine(String line) {
        List<String> values = new ArrayList<>();
        StringBuilder value = new StringBuilder();
        boolean quoted = false;
        for (int index = 0; index < line.length(); index++) {
            char character = line.charAt(index);
            if (character == '"') {
                quoted = !quoted;
            } else if (character == ',' && !quoted) {
                values.add(value.toString());
                value.setLength(0);
            } else {
                value.append(character);
            }
        }
        values.add(value.toString());
        return values;
    }

    private Object parseValue(String value) {
        if (value.isBlank()) {
            return "";
        }
        try {
            return Double.parseDouble(value);
        } catch (NumberFormatException exception) {
            return value;
        }
    }
}
