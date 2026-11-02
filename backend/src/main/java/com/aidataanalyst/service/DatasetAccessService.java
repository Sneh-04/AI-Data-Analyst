package com.aidataanalyst.service;

import com.aidataanalyst.entity.Dataset;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.DatasetRepository;
import com.aidataanalyst.repository.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;

@Service
public class DatasetAccessService {

    private final DatasetRepository datasetRepository;
    private final UserRepository userRepository;

    public DatasetAccessService(DatasetRepository datasetRepository, UserRepository userRepository) {
        this.datasetRepository = datasetRepository;
        this.userRepository = userRepository;
    }

    public Dataset requireOwnedDataset(Long datasetId, String email) {
        User user = requireUser(email);
        return datasetRepository.findByIdAndUploadedByAndDeletionStatus(datasetId, user.getId(), "ACTIVE")
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Dataset not found"));
    }

    public List<Dataset> listOwnedDatasets(String email) {
        User user = requireUser(email);
        return datasetRepository.findAllByUploadedByOrderByCreatedAtDescIdDesc(user.getId());
    }

    private User requireUser(String email) {
        return userRepository.findByEmailIgnoreCase(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "User is unavailable"));
    }
}
