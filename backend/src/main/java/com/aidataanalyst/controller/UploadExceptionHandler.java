package com.aidataanalyst.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

import java.util.Map;

@RestControllerAdvice
public class UploadExceptionHandler {

    private final String maxUploadSize;

    public UploadExceptionHandler(
            @Value("${spring.servlet.multipart.max-file-size:20MB}") String maxUploadSize) {
        this.maxUploadSize = maxUploadSize;
    }

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<Map<String, String>> handleMaxUploadSizeExceeded(MaxUploadSizeExceededException exception) {
        return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE)
                .body(Map.of("message", "File exceeds the maximum upload size of " + maxUploadSize + "."));
    }
}
