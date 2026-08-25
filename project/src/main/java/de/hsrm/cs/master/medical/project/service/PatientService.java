package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.*;
import de.hsrm.cs.master.medical.project.exception.ResourceNotFoundException;
import de.hsrm.cs.master.medical.project.forms.MedicationForm;
import de.hsrm.cs.master.medical.project.forms.PatientForm;
import de.hsrm.cs.master.medical.project.mapper.PatientMapper;
import de.hsrm.cs.master.medical.project.repository.PatientRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class PatientService {

    @Autowired
    private PatientRepository patientRepository;

    @Autowired
    private FileStorageService fileStorageService;

    @Autowired
    private PatientMapper mapper;

    @Transactional(readOnly = true)
    public List<Patient> findAll() {
        return patientRepository.findAll(org.springframework.data.domain.Sort.by("id"));
    }

    @Transactional(readOnly = true)
    public Patient getOrThrow(Long id) {
        return patientRepository.findById(id).orElseThrow(() -> new ResourceNotFoundException("No patient found with ID " + id + "."));
    }

    public Patient create(PatientForm form) {
        Patient patient = new Patient();
        mapper.updatePatient(form, patient);
        return patientRepository.save(patient);
    }

    public Patient update(Long id, PatientForm form) {
        Patient patient = getOrThrow(id);
        mapper.updatePatient(form, patient);
        return patientRepository.save(patient);
    }

    public void delete(Long id) {
        Patient patient = getOrThrow(id);

        for (HistoryEntry entry : patient.getHistoryEntries()) {
            for (Attachment attachment : entry.getAttachments()) {
                fileStorageService.delete(attachment.getStoredPath());
            }
            if (entry.getStudy() != null) {
                for (XRayImage image : entry.getStudy().getXrayImages()) {
                    for (String key : image.getPrediction().getGradCamPaths().keySet()) {
                        String filepath = image.getPrediction().getGradCamPaths().get(key);
                        fileStorageService.delete(filepath);
                    }
                    fileStorageService.delete(image.getStoredPath());
                }
            }
        }

        patientRepository.delete(patient);
    }
}
