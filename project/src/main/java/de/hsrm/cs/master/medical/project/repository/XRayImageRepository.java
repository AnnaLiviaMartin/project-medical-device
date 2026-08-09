package de.hsrm.cs.master.medical.project.repository;

import de.hsrm.cs.master.medical.project.domain.XRayImage;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface XRayImageRepository extends JpaRepository<XRayImage, Long> {
    List<XRayImage> findByStudyIdOrderByUploadedAtDesc(Long studyId);
}
