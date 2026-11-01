package com.aidataanalyst.security;

import org.junit.jupiter.api.Test;
import org.springframework.boot.web.servlet.FilterRegistrationBean;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.Mockito.mock;

class SecurityConfigTest {

    @Test
    void jwtFilterIsNotRegisteredOutsideTheSpringSecurityChain() {
        JwtAuthFilter jwtAuthFilter = mock(JwtAuthFilter.class);

        FilterRegistrationBean<JwtAuthFilter> registration =
                new SecurityConfig(jwtAuthFilter).jwtAuthFilterServletRegistration();

        assertFalse(registration.isEnabled());
    }
}
