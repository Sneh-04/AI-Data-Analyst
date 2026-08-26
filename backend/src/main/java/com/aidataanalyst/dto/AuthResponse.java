package com.aidataanalyst.dto;

public record AuthResponse(
        String token,
        String email,
        String fullName,
        String role
) {
}
