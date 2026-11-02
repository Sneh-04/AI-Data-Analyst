package com.aidataanalyst.service;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.UserRepository;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertSame;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DatasetAccessServiceListTest {

    @Test
    void listsCurrentUsersDatasetsInNewestFirstOrder() {
        DatasetRepository datasetRepository = mock(DatasetRepository.class);
        UserRepository userRepository = mock(UserRepository.class);
        User user = mock(User.class);
        when(user.getId()).thenReturn(42L);
        when(userRepository.findByEmailIgnoreCase("analyst@example.test")).thenReturn(Optional.of(user));
        List<Dataset> datasets = List.of(mock(Dataset.class), mock(Dataset.class));
        when(datasetRepository.findAllByUploadedByOrderByCreatedAtDescIdDesc(42L)).thenReturn(datasets);
        DatasetAccessService service = new DatasetAccessService(datasetRepository, userRepository);

        assertSame(datasets, service.listOwnedDatasets("analyst@example.test"));

        verify(datasetRepository).findAllByUploadedByOrderByCreatedAtDescIdDesc(42L);
    }
}
