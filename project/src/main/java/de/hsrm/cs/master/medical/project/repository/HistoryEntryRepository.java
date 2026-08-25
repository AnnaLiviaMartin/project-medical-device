package de.hsrm.cs.master.medical.project.repository;

import de.hsrm.cs.master.medical.project.domain.HistoryEntry;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface HistoryEntryRepository extends JpaRepository<HistoryEntry, Long> {
    List<HistoryEntry> findByPatientIdOrderByDateDesc(Long patientId);
}
