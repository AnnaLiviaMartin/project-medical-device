package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.*;
import de.hsrm.cs.master.medical.project.exception.ResourceNotFoundException;
import de.hsrm.cs.master.medical.project.repository.*;
import de.hsrm.cs.master.medical.project.forms.MedicationForm;
import de.hsrm.cs.master.medical.project.forms.PatientForm;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class PatientService {

    // TODO applyForm und toForm auslagern wohin

    @Autowired
    private PatientRepository patientRepository;

    @Transactional(readOnly = true)
    public List<Patient> findAll() {
        return patientRepository.findAll(org.springframework.data.domain.Sort.by("id"));
    }

    @Transactional(readOnly = true)
    public Patient getOrThrow(Long id) {
        return patientRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("No patient found with ID " + id + "."));
    }

    public Patient create(PatientForm form) {
        Patient patient = new Patient();
        applyForm(patient, form);
        return patientRepository.save(patient);
    }

    public Patient update(Long id, PatientForm form) {
        Patient patient = getOrThrow(id);
        applyForm(patient, form);
        return patientRepository.save(patient);
    }

    public void delete(Long id) {
        Patient patient = getOrThrow(id);
        patientRepository.delete(patient);
    }

    private void applyForm(Patient patient, PatientForm form) {
        patient.setFirstName(form.getFirstName().trim());
        patient.setLastName(form.getLastName().trim());
        patient.setDateOfBirth(form.getDateOfBirth());
        patient.setSex(form.getSex());
        patient.setDiagnosis(form.getDiagnosis().trim());
        patient.setStatus(form.getStatus());
        patient.setLastVisit(form.getLastVisit());
        patient.setNextAppointment(form.getNextAppointment());
        patient.setDoctor(form.getDoctor().trim());
        patient.setWard(nullToEmpty(form.getWard()));

        patient.setAddressStreet(nullToEmpty(form.getAddressStreet()));
        patient.setAddressZip(nullToEmpty(form.getAddressZip()));
        patient.setAddressCity(nullToEmpty(form.getAddressCity()));

        patient.setEmergencyContactName(nullToEmpty(form.getEmergencyContactName()));
        patient.setEmergencyContactRelation(nullToEmpty(form.getEmergencyContactRelation()));
        patient.setEmergencyContactPhone(nullToEmpty(form.getEmergencyContactPhone()));

        patient.setInsuranceProvider(nullToEmpty(form.getInsuranceProvider()));
        patient.setInsurancePolicyNumber(nullToEmpty(form.getInsurancePolicyNumber()));

        patient.getAllergies().clear();
        for (String allergyName : form.parsedAllergies()) {
            patient.getAllergies().add(new Allergy(patient, allergyName));
        }

        patient.getMedications().clear();
        for (MedicationForm medicationForm : form.nonEmptyMedications()) {
            patient.getMedications().add(new Medication(
                    patient,
                    medicationForm.getName().trim(),
                    medicationForm.getDosage().trim(),
                    medicationForm.getSchedule().trim()
            ));
        }
    }

    private String nullToEmpty(String value) {
        return value == null ? "" : value.trim();
    }

    /** Baut aus einer bestehenden Patient-Entity ein vorausgefuelltes Formular fuer die Edit-Seite. */
    public PatientForm toForm(Patient patient) {
        PatientForm form = new PatientForm();
        form.setFirstName(patient.getFirstName());
        form.setLastName(patient.getLastName());
        form.setDateOfBirth(patient.getDateOfBirth());
        form.setSex(patient.getSex());
        form.setDiagnosis(patient.getDiagnosis());
        form.setStatus(patient.getStatus());
        form.setLastVisit(patient.getLastVisit());
        form.setNextAppointment(patient.getNextAppointment());
        form.setDoctor(patient.getDoctor());
        form.setWard(patient.getWard());

        form.setAddressStreet(patient.getAddressStreet());
        form.setAddressZip(patient.getAddressZip());
        form.setAddressCity(patient.getAddressCity());

        form.setEmergencyContactName(patient.getEmergencyContactName());
        form.setEmergencyContactRelation(patient.getEmergencyContactRelation());
        form.setEmergencyContactPhone(patient.getEmergencyContactPhone());

        form.setInsuranceProvider(patient.getInsuranceProvider());
        form.setInsurancePolicyNumber(patient.getInsurancePolicyNumber());

        form.setAllergiesRaw(String.join("\n", patient.getAllergies().stream().map(Allergy::getName).toList()));

        List<MedicationForm> medicationForms = patient.getMedications().stream().map(m -> {
            MedicationForm mf = new MedicationForm();
            mf.setName(m.getName());
            mf.setDosage(m.getDosage());
            mf.setSchedule(m.getSchedule());
            return mf;
        }).collect(java.util.stream.Collectors.toCollection(java.util.ArrayList::new));
        if (medicationForms.isEmpty()) {
            medicationForms.add(new MedicationForm());
        }
        form.setMedications(medicationForms);

        return form;
    }
}
