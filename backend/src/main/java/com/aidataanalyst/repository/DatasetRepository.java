package com.aidataanalyst.repository;

import com.aidataanalyst.entity.Dataset;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface DatasetRepository extends JpaRepository<Dataset, Long> {
    Optional<Dataset> findByIdAndUploadedBy(Long id, Long uploadedBy);

    Optional<Dataset> findByIdAndUploadedByAndDeletionStatus(Long id, Long uploadedBy, String deletionStatus);

    List<Dataset> findAllByUploadedByOrderByCreatedAtDescIdDesc(Long uploadedBy);

    List<Dataset> findAllByUploadedByAndDeletionStatusOrderByCreatedAtDescIdDesc(
            Long uploadedBy, String deletionStatus);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select d from Dataset d where d.id = :datasetId and d.uploadedBy = :userId")
    Optional<Dataset> findOwnedByIdForUpdate(@Param("datasetId") Long datasetId, @Param("userId") Long userId);

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select d from Dataset d where d.id = :datasetId and d.uploadedBy = :userId "
            + "and d.deletionStatus = 'ACTIVE'")
    Optional<Dataset> findActiveOwnedByIdForUpdate(
            @Param("datasetId") Long datasetId, @Param("userId") Long userId);
}
