package com.aidataanalyst.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class DatasetStorageServiceTest {

    @TempDir
    Path storageRoot;

    @Test
    void storesFilesInNestedDirectories() throws Exception {
        DatasetStorageService service = new DatasetStorageService(storageRoot.toString());
        byte[] content = "report".getBytes(java.nio.charset.StandardCharsets.UTF_8);

        Path stored = service.store("reports/report.pdf", content);

        assertTrue(Files.isRegularFile(stored));
        assertArrayEquals(content, Files.readAllBytes(stored));
    }

    @Test
    void deletesFilesIdempotentlyAndRejectsPathsOutsideStorageRoot() throws Exception {
        DatasetStorageService service = new DatasetStorageService(storageRoot.toString());
        Path stored = service.store("reports/report.pdf", "report".getBytes(java.nio.charset.StandardCharsets.UTF_8));

        service.delete("reports/report.pdf");
        service.delete("reports/report.pdf");

        assertTrue(Files.notExists(stored));
        assertThrows(java.io.IOException.class, () -> service.delete("../outside.csv"));
    }
}
