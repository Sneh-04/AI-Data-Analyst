package com.aidataanalyst.service;

import com.aidataanalyst.entity.Forecast;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.ForecastRepository;
import com.aidataanalyst.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class ForecastPersistenceServiceTest {

    @Test
    void persistsForecastRowsAsJsonObjects() {
        ForecastRepository forecastRepository = mock(ForecastRepository.class);
        UserRepository userRepository = mock(UserRepository.class);
        User user = new User("analyst@example.invalid", "hash", "Analyst");
        when(userRepository.findByEmailIgnoreCase("analyst@example.invalid"))
                .thenReturn(Optional.of(user));
        when(forecastRepository.save(any(Forecast.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));
        ForecastPersistenceService service =
                new ForecastPersistenceService(forecastRepository, userRepository);
        List<Map<String, Object>> rows = List.of(Map.of("period", 1, "value", 12.5));

        service.saveForecast(
                7L,
                "date",
                "value",
                Map.of("model_used", "naive", "forecast", rows),
                "analyst@example.invalid");

        ArgumentCaptor<Forecast> forecast = ArgumentCaptor.forClass(Forecast.class);
        verify(forecastRepository).save(forecast.capture());
        assertEquals(rows, forecast.getValue().getForecastJson());
    }
}
