package com.aidataanalyst.service;

import com.aidataanalyst.entity.Forecast;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.ForecastRepository;
import com.aidataanalyst.repository.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class ForecastPersistenceService {

    private final ForecastRepository forecastRepository;
    private final UserRepository userRepository;

    public ForecastPersistenceService(ForecastRepository forecastRepository, UserRepository userRepository) {
        this.forecastRepository = forecastRepository;
        this.userRepository = userRepository;
    }

    @Transactional
    public Forecast saveForecast(Long datasetId, String dateColumn, String valueColumn,
                                Map<String, Object> mlServiceResponse, String email) {
        User user = userRepository.findByEmailIgnoreCase(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "User is unavailable"));
        Object rawForecast = mlServiceResponse.get("forecast");
        if (!(rawForecast instanceof java.util.List<?>)) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Forecast response has no forecast data");
        }

        Map<String, Object> modelComparison = toStringKeyedMap(mlServiceResponse.get("model_comparison"));
        String modelUsed = mlServiceResponse.get("model_used") instanceof String value ? value : null;
        Forecast forecast = new Forecast(datasetId, dateColumn, valueColumn, modelUsed,
                modelComparison, rawForecast, user.getId());
        return forecastRepository.save(forecast);
    }

    private Map<String, Object> toStringKeyedMap(Object value) {
        if (!(value instanceof Map<?, ?> rawMap)) {
            return null;
        }
        Map<String, Object> result = new LinkedHashMap<>();
        rawMap.forEach((key, item) -> result.put(String.valueOf(key), item));
        return result;
    }
}