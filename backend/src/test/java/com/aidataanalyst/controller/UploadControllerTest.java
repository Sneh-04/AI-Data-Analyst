package com.aidataanalyst.controller;

import com.aidataanalyst.entity.User;
import com.aidataanalyst.entity.Workspace;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.UserRepository;
import com.aidataanalyst.repository.WorkspaceRepository;
import com.aidataanalyst.service.DatasetStorageService;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.security.core.Authentication;
import org.springframework.web.server.ResponseStatusException;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

class UploadControllerTest {

    @Test
    void rejectsNonRectangularCsvWithBadRequestBeforeStoringIt() {
        DatasetStorageService storageService = mock(DatasetStorageService.class);
        UserRepository userRepository = mock(UserRepository.class);
        WorkspaceRepository workspaceRepository = mock(WorkspaceRepository.class);
        User user = mock(User.class);
        when(userRepository.findByEmailIgnoreCase("analyst@example.test")).thenReturn(Optional.of(user));
        when(workspaceRepository.findFirstByOwnerIdOrderByIdAsc(user.getId()))
                .thenReturn(Optional.of(mock(Workspace.class)));
        Authentication authentication = mock(Authentication.class);
        when(authentication.getName()).thenReturn("analyst@example.test");
        UploadController controller = new UploadController(
                mock(DatasetRepository.class), storageService, userRepository, workspaceRepository);
        MockMultipartFile file = new MockMultipartFile(
                "file", "dataset.csv", "text/csv", "name,value\nitem,1,extra".getBytes());

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> controller.upload(file, authentication));

        assertEquals(400, exception.getStatusCode().value());
        assertEquals("CSV row 2 has 3 columns; expected 2.", exception.getReason());
        verifyNoInteractions(storageService);
    }
}
