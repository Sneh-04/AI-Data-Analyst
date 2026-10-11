package com.aidataanalyst.service;

import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.web.server.ResponseStatusException;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DatasetAccessServiceTest {

    @Test
    void rejectsDatasetLookupForAnotherUserWithoutRevealingItsExistence() {
        DatasetRepository datasetRepository = mock(DatasetRepository.class);
        UserRepository userRepository = mock(UserRepository.class);
        User user = mock(User.class);
        when(user.getId()).thenReturn(42L);
        when(userRepository.findByEmailIgnoreCase("analyst@example.test")).thenReturn(Optional.of(user));
        when(datasetRepository.findByIdAndUploadedBy(17L, 42L)).thenReturn(Optional.empty());
        DatasetAccessService accessService = new DatasetAccessService(datasetRepository, userRepository);

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> accessService.requireOwnedDataset(17L, "analyst@example.test"));

        assertEquals(404, exception.getStatusCode().value());
        verify(datasetRepository).findByIdAndUploadedBy(17L, 42L);
    }
}
