package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.Patient;
import de.hsrm.cs.master.medical.project.domain.PatientStatus;
import de.hsrm.cs.master.medical.project.domain.Sex;
import de.hsrm.cs.master.medical.project.exception.ResourceNotFoundException;
import de.hsrm.cs.master.medical.project.forms.MedicationForm;
import de.hsrm.cs.master.medical.project.forms.PatientForm;
import de.hsrm.cs.master.medical.project.repository.PatientRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Sort;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PatientServiceTest {

    @Mock
    private PatientRepository patientRepository;

    @InjectMocks
    private PatientService patientService;

    private Patient existingPatient;

    @BeforeEach
    void setUp() {
        existingPatient = new Patient();
        existingPatient.setId(1L);
        existingPatient.setFirstName("Anna");
        existingPatient.setLastName("Becker");
        existingPatient.setDateOfBirth(LocalDate.of(1990, 1, 1));
        existingPatient.setSex(Sex.FEMALE);
        existingPatient.setDiagnosis("Hypertension");
        existingPatient.setStatus(PatientStatus.OUTPATIENT);
        existingPatient.setLastVisit(LocalDate.of(2026, 1, 1));
        existingPatient.setDoctor("Dr. Klein");
    }

    @Test
    void findAll_delegatesToRepository_sortedById() {
        when(patientRepository.findAll(any(Sort.class))).thenReturn(List.of(existingPatient));

        List<Patient> result = patientService.findAll();

        assertThat(result).containsExactly(existingPatient);
        verify(patientRepository).findAll(Sort.by("id"));
    }

    @Test
    void getOrThrow_returnsPatient_whenPresent() {
        when(patientRepository.findById(1L)).thenReturn(Optional.of(existingPatient));

        Patient result = patientService.getOrThrow(1L);

        assertThat(result).isSameAs(existingPatient);
    }

    @Test
    void getOrThrow_throwsResourceNotFoundException_whenMissing() {
        when(patientRepository.findById(42L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> patientService.getOrThrow(42L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("42");
    }

    @Test
    void create_mapsFormFieldsOntoNewPatient_andSaves() {
        PatientForm form = validForm();
        form.setAllergiesRaw("Penicillin\n  \nLatex\n");

        MedicationForm med = new MedicationForm();
        med.setName(" Metformin ");
        med.setDosage(" 1000 mg ");
        med.setSchedule(" 2x daily ");
        MedicationForm blankRow = new MedicationForm(); // simulates the leftover "+ Add" row
        form.setMedications(List.of(med, blankRow));

        when(patientRepository.save(any(Patient.class))).thenAnswer(inv -> inv.getArgument(0));

        Patient saved = patientService.create(form);

        assertThat(saved.getFirstName()).isEqualTo("Anna");
        assertThat(saved.getLastName()).isEqualTo("Becker");
        assertThat(saved.getDiagnosis()).isEqualTo("Hypertension");
        assertThat(saved.getStatus()).isEqualTo(PatientStatus.OUTPATIENT);

        // Allergies: trimmed, blank lines dropped
        assertThat(saved.getAllergies()).extracting("name").containsExactly("Penicillin", "Latex");
        assertThat(saved.getAllergies()).allMatch(a -> a.getPatient() == saved);

        // Medications: blank row filtered out, values trimmed
        assertThat(saved.getMedications()).hasSize(1);
        assertThat(saved.getMedications().get(0).getName()).isEqualTo("Metformin");
        assertThat(saved.getMedications().get(0).getDosage()).isEqualTo("1000 mg");
        assertThat(saved.getMedications().get(0).getSchedule()).isEqualTo("2x daily");

        verify(patientRepository).save(saved);
    }

    @Test
    void create_blankOptionalFields_areStoredAsEmptyString_notNull() {
        PatientForm form = validForm();
        form.setWard(null);
        form.setAddressStreet(null);
        form.setInsuranceProvider(null);

        when(patientRepository.save(any(Patient.class))).thenAnswer(inv -> inv.getArgument(0));

        Patient saved = patientService.create(form);

        assertThat(saved.getWard()).isEmpty();
        assertThat(saved.getAddressStreet()).isEmpty();
        assertThat(saved.getInsuranceProvider()).isEmpty();
    }

    @Test
    void update_loadsExistingPatient_appliesFormAndSaves() {
        when(patientRepository.findById(1L)).thenReturn(Optional.of(existingPatient));
        when(patientRepository.save(any(Patient.class))).thenAnswer(inv -> inv.getArgument(0));

        PatientForm form = validForm();
        form.setDiagnosis("Updated diagnosis");

        Patient updated = patientService.update(1L, form);

        assertThat(updated).isSameAs(existingPatient);
        assertThat(updated.getDiagnosis()).isEqualTo("Updated diagnosis");
        verify(patientRepository).save(existingPatient);
    }

    @Test
    void update_throwsResourceNotFoundException_whenPatientMissing() {
        when(patientRepository.findById(99L)).thenReturn(Optional.empty());
        PatientForm form = validForm();

        assertThatThrownBy(() -> patientService.update(99L, form))
                .isInstanceOf(ResourceNotFoundException.class);

        verify(patientRepository, never()).save(any());
    }

    @Test
    void delete_looksUpThenDeletesPatient() {
        when(patientRepository.findById(1L)).thenReturn(Optional.of(existingPatient));

        patientService.delete(1L);

        ArgumentCaptor<Patient> captor = ArgumentCaptor.forClass(Patient.class);
        verify(patientRepository).delete(captor.capture());
        assertThat(captor.getValue()).isSameAs(existingPatient);
    }

    @Test
    void delete_throwsResourceNotFoundException_whenPatientMissing() {
        when(patientRepository.findById(7L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> patientService.delete(7L))
                .isInstanceOf(ResourceNotFoundException.class);

        verify(patientRepository, never()).delete(any());
    }

    @Test
    void toForm_prefillsFormFromExistingPatient_andAddsEmptyMedicationRow_whenNoneExist() {
        existingPatient.getAllergies().clear();
        existingPatient.getMedications().clear();

        PatientForm form = patientService.toForm(existingPatient);

        assertThat(form.getFirstName()).isEqualTo("Anna");
        assertThat(form.getLastName()).isEqualTo("Becker");
        assertThat(form.getSex()).isEqualTo(Sex.FEMALE);
        // No medications on record -> the edit form still needs one empty row for the "+" UI
        assertThat(form.getMedications()).hasSize(1);
        assertThat(form.getMedications().get(0).isBlank()).isTrue();
    }

    private PatientForm validForm() {
        PatientForm form = new PatientForm();
        form.setFirstName("Anna");
        form.setLastName("Becker");
        form.setDateOfBirth(LocalDate.of(1990, 1, 1));
        form.setSex(Sex.FEMALE);
        form.setDiagnosis("Hypertension");
        form.setStatus(PatientStatus.OUTPATIENT);
        form.setLastVisit(LocalDate.of(2026, 1, 1));
        form.setDoctor("Dr. Klein");
        return form;
    }
}
