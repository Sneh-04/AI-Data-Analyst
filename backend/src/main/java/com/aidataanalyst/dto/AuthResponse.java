package com.aidataanalyst.dto;

public record AuthResponse(
        String token,
        String refreshToken,
        String email,
        String fullName,
        String role
) {
}
