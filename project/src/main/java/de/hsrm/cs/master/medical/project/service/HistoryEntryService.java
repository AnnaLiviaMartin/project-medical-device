package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.HistoryEntry;
import de.hsrm.cs.master.medical.project.domain.Patient;
import de.hsrm.cs.master.medical.project.exception.ResourceNotFoundException;
import de.hsrm.cs.master.medical.project.forms.HistoryEntryForm;
import de.hsrm.cs.master.medical.project.repository.HistoryEntryRepository;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class HistoryEntryService {

    @Autowired
    private HistoryEntryRepository historyEntryRepository;

    @Autowired
    private PatientService patientService;

    @Transactional(readOnly = true)
    public List<HistoryEntry> findByPatient(Long patientId) {
        return historyEntryRepository.findByPatientIdOrderByDateDesc(patientId);
    }

    @Transactional(readOnly = true)
    public HistoryEntry getOrThrow(Long entryId) {
        return historyEntryRepository.findById(entryId)
                .orElseThrow(() -> new ResourceNotFoundException("No history entry found with ID " + entryId + "."));
    }

    @Transactional(readOnly = true)
    public HistoryEntry getOrThrowForPatient(Long patientId, Long entryId) {
        HistoryEntry entry = getOrThrow(entryId);
        if (!entry.getPatient().getId().equals(patientId)) {
            throw new ResourceNotFoundException("No history entry found with ID " + entryId + " for this patient.");
        }
        return entry;
    }

    public HistoryEntry create(Long patientId, @Valid HistoryEntryForm form) {
        Patient patient = patientService.getOrThrow(patientId);

        HistoryEntry entry = new HistoryEntry();
        entry.setPatient(patient);
        entry.setDate(form.getDate());
        entry.setTitle(form.getTitle().trim());
        entry.setCategory(form.getCategory());
        entry.setDescription(form.getDescription() == null ? "" : form.getDescription().trim());
        entry.setDoctor(form.getDoctor() == null ? "" : form.getDoctor().trim());
        entry.setDepartment(form.getDepartment() == null ? "" : form.getDepartment().trim());

        return save(entry);
    }

    public HistoryEntry save(HistoryEntry entry) {
        return historyEntryRepository.save(entry);
    }
}
