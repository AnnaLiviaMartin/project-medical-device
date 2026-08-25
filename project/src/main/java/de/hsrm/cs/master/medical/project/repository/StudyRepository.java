package de.hsrm.cs.master.medical.project.repository;

import de.hsrm.cs.master.medical.project.domain.Study;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StudyRepository extends JpaRepository<Study, Long> {
}
