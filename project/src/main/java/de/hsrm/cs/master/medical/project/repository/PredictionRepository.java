package de.hsrm.cs.master.medical.project.repository;

import de.hsrm.cs.master.medical.project.domain.Prediction;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface PredictionRepository extends JpaRepository<Prediction, Long> {
    Optional<Prediction> findByXrayImageId(Long xrayImageId);
}
