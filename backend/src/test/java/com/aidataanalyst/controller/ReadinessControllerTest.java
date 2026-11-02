package com.aidataanalyst.controller;

import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class ReadinessControllerTest {

    @Test
    void reportsReadyOnlyAfterDatabaseQuerySucceeds() {
        JdbcTemplate jdbcTemplate = mock(JdbcTemplate.class);
        when(jdbcTemplate.queryForObject("SELECT 1", Integer.class)).thenReturn(1);

        var response = new ReadinessController(jdbcTemplate).readiness();

        assertEquals("UP", response.get("status"));
        verify(jdbcTemplate).queryForObject("SELECT 1", Integer.class);
    }
}
