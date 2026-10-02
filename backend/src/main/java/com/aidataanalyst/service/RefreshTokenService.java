package com.aidataanalyst.service;

import com.aidataanalyst.entity.RefreshToken;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.RefreshTokenRepository;
import com.aidataanalyst.repository.UserRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.Base64;

/**
 * Issues opaque, DB-backed refresh tokens (not JWTs) so individual sessions can
 * be revoked server-side — a signed JWT refresh token cannot be invalidated
 * before its own expiry without a denylist, which this avoids entirely.
 *
 * Each successful refresh ROTATES the token (old one revoked, new one issued).
 * Rotation means a stolen-and-reused old token is a detectable signal — if it's
 * ever presented again after rotation, it will already be revoked.
 */
@Service
public class RefreshTokenService {

    private static final SecureRandom SECURE_RANDOM = new SecureRandom();

    private final RefreshTokenRepository refreshTokenRepository;
    private final UserRepository userRepository;
    private final long refreshExpirationMs;

    public RefreshTokenService(
            RefreshTokenRepository refreshTokenRepository,
            UserRepository userRepository,
            @Value("${jwt.refresh-expiration-ms}") long refreshExpirationMs) {
        this.refreshTokenRepository = refreshTokenRepository;
        this.userRepository = userRepository;
        this.refreshExpirationMs = refreshExpirationMs;
    }

    @Transactional
    public String issue(Long userId) {
        String rawToken = generateRawToken();
        RefreshToken entity = new RefreshToken(
                userId,
                hash(rawToken),
                Instant.now().plusMillis(refreshExpirationMs));
        refreshTokenRepository.save(entity);
        return rawToken;
    }

    /**
     * Validates the presented raw token, revokes it, and issues a replacement
     * for the same user. Returns the resolved User and the new raw refresh
     * token so the caller can mint a fresh access token alongside it.
     */
    @Transactional
    public RotationResult validateAndRotate(String rawToken) {
        RefreshToken existing = refreshTokenRepository.findByTokenHash(hash(rawToken))
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid refresh token"));

        if (!existing.isUsable()) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Refresh token is expired or revoked");
        }

        User user = userRepository.findById(existing.getUserId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "User is unavailable"));

        existing.revoke();
        refreshTokenRepository.save(existing);

        String newRawToken = issue(user.getId());
        return new RotationResult(user, newRawToken);
    }

    @Transactional
    public void revoke(String rawToken) {
        refreshTokenRepository.findByTokenHash(hash(rawToken))
                .ifPresent(token -> {
                    token.revoke();
                    refreshTokenRepository.save(token);
                });
        // Silently no-op if the token is unknown/already revoked — logout should
        // never fail just because the session was already gone.
    }

    private String generateRawToken() {
        byte[] bytes = new byte[32];
        SECURE_RANDOM.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    private String hash(String rawToken) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(rawToken.getBytes(StandardCharsets.UTF_8));
            StringBuilder hex = new StringBuilder();
            for (byte b : digest) {
                hex.append(String.format("%02x", b));
            }
            return hex.toString();
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is unavailable", exception);
        }
    }

    public record RotationResult(User user, String rawRefreshToken) {
    }
}
