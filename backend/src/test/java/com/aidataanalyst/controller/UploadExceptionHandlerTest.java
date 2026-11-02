package com.aidataanalyst.controller;

import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

class UploadExceptionHandlerTest {

    @Test
    void returnsClearPayloadTooLargeMessage() {
        UploadExceptionHandler handler = new UploadExceptionHandler("20MB");

        var response = handler.handleMaxUploadSizeExceeded(mock(MaxUploadSizeExceededException.class));

        assertEquals(HttpStatus.PAYLOAD_TOO_LARGE, response.getStatusCode());
        assertEquals("File exceeds the maximum upload size of 20MB.", response.getBody().get("message"));
    }
}
