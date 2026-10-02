package com.aidataanalyst.controller;

import com.aidataanalyst.dto.AuthResponse;
import com.aidataanalyst.dto.LoginRequest;
import com.aidataanalyst.dto.RefreshTokenRequest;
import com.aidataanalyst.dto.RegisterRequest;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.security.JwtService;
import com.aidataanalyst.service.RefreshTokenService;
import com.aidataanalyst.service.UserService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final UserService userService;
    private final JwtService jwtService;
    private final RefreshTokenService refreshTokenService;

    public AuthController(UserService userService, JwtService jwtService, RefreshTokenService refreshTokenService) {
        this.userService = userService;
        this.jwtService = jwtService;
        this.refreshTokenService = refreshTokenService;
    }

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        User user = userService.register(request.email(), request.password(), request.fullName());
        return ResponseEntity.status(HttpStatus.CREATED).body(toResponse(user));
    }

    @PostMapping("/login")
    public AuthResponse login(@Valid @RequestBody LoginRequest request) {
        return toResponse(userService.authenticate(request.email(), request.password()));
    }

    /**
     * Exchanges a still-valid refresh token for a new access token, rotating
     * the refresh token in the process (old one revoked, new one returned).
     * Lets the frontend silently renew a session instead of forcing re-login
     * every time the short-lived access token expires.
     */
    @PostMapping("/refresh")
    public AuthResponse refresh(@Valid @RequestBody RefreshTokenRequest request) {
        RefreshTokenService.RotationResult result = refreshTokenService.validateAndRotate(request.refreshToken());
        User user = result.user();
        return new AuthResponse(
                jwtService.generateToken(user.getEmail()),
                result.rawRefreshToken(),
                user.getEmail(),
                user.getFullName(),
                user.getRole());
    }

    /**
     * Revokes a refresh token server-side so it can no longer be exchanged for
     * a new access token, even if it hasn't expired yet. Always returns 200 —
     * logging out of an already-expired/unknown session is not an error.
     */
    @PostMapping("/logout")
    public ResponseEntity<Map<String, String>> logout(@Valid @RequestBody RefreshTokenRequest request) {
        refreshTokenService.revoke(request.refreshToken());
        return ResponseEntity.ok(Map.of("message", "Logged out"));
    }

    private AuthResponse toResponse(User user) {
        String refreshToken = refreshTokenService.issue(user.getId());
        return new AuthResponse(
                jwtService.generateToken(user.getEmail()),
                refreshToken,
                user.getEmail(),
                user.getFullName(),
                user.getRole());
    }
}
