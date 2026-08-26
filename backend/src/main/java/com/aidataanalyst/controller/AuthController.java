package com.aidataanalyst.controller;

import com.aidataanalyst.dto.AuthResponse;
import com.aidataanalyst.dto.LoginRequest;
import com.aidataanalyst.dto.RegisterRequest;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.security.JwtService;
import com.aidataanalyst.service.UserService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final UserService userService;
    private final JwtService jwtService;

    public AuthController(UserService userService, JwtService jwtService) {
        this.userService = userService;
        this.jwtService = jwtService;
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

    private AuthResponse toResponse(User user) {
        return new AuthResponse(
                jwtService.generateToken(user.getEmail()),
                user.getEmail(),
                user.getFullName(),
                user.getRole());
    }
}
