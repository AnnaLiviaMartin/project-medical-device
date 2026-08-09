package de.hsrm.cs.master.medical.project.repository;

import de.hsrm.cs.master.medical.project.domain.Patient;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PatientRepository extends JpaRepository<Patient, Long> {
}
