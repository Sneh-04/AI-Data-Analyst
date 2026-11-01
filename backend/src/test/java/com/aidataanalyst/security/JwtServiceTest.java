package com.aidataanalyst.security;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.Test;

import java.nio.charset.StandardCharsets;
import java.util.Date;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JwtServiceTest {

    @Test
    void rejectsSigningSecretsShorterThan256Bits() {
        assertThrows(IllegalArgumentException.class, () -> new JwtService("short-secret", 60_000));
    }

    @Test
    void signsAndValidatesTokensWithA256BitSecret() {
        JwtService service = new JwtService("0123456789abcdef0123456789abcdef", 60_000);
        String token = service.generateToken("analyst@example.invalid");

        assertTrue(service.isTokenValid(token, "analyst@example.invalid"));
        assertFalse(service.isTokenValid(token, "other@example.invalid"));
    }

    @Test
    void rejectsTokensWhoseLifetimeExceedsConfiguredAccessTokenLifetime() {
        String secret = "0123456789abcdef0123456789abcdef";
        long configuredLifetimeMs = 60_000;
        Date issuedAt = new Date();
        String token = Jwts.builder()
                .subject("analyst@example.invalid")
                .issuedAt(issuedAt)
                .expiration(new Date(issuedAt.getTime() + configuredLifetimeMs + 2_000))
                .signWith(Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8)))
                .compact();

        assertFalse(new JwtService(secret, configuredLifetimeMs)
                .isTokenValid(token, "analyst@example.invalid"));
    }

    @Test
    void rejectsTokensIssuedInTheFuture() {
        String secret = "0123456789abcdef0123456789abcdef";
        Date issuedAt = new Date(System.currentTimeMillis() + 60_000);
        String token = Jwts.builder()
                .subject("analyst@example.invalid")
                .issuedAt(issuedAt)
                .expiration(new Date(issuedAt.getTime() + 60_000))
                .signWith(Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8)))
                .compact();

        assertFalse(new JwtService(secret, 60_000).isTokenValid(token, "analyst@example.invalid"));
    }
}
