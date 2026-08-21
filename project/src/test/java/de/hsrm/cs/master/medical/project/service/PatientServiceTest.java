package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.Patient;
import de.hsrm.cs.master.medical.project.domain.PatientStatus;
import de.hsrm.cs.master.medical.project.domain.Sex;
import de.hsrm.cs.master.medical.project.exception.ResourceNotFoundException;
import de.hsrm.cs.master.medical.project.forms.PatientForm;
import de.hsrm.cs.master.medical.project.mapper.PatientMapper;
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

    @Mock
    private PatientMapper mapper;

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

        assertThatThrownBy(() -> patientService.getOrThrow(42L)).isInstanceOf(ResourceNotFoundException.class).hasMessageContaining("42");
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
    void update_loadsExistingPatient_mapsAndSaves() {
        when(patientRepository.findById(1L)).thenReturn(Optional.of(existingPatient));
        when(patientRepository.save(any(Patient.class))).thenAnswer(inv -> inv.getArgument(0));

        PatientForm form = validForm();

        Patient updated = patientService.update(1L, form);

        assertThat(updated).isSameAs(existingPatient);

        verify(patientRepository).findById(1L);
        verify(mapper).updatePatient(form, existingPatient);
        verify(patientRepository).save(existingPatient);
    }

    @Test
    void update_throwsResourceNotFoundException_whenPatientMissing() {
        when(patientRepository.findById(99L)).thenReturn(Optional.empty());
        PatientForm form = validForm();

        assertThatThrownBy(() -> patientService.update(99L, form)).isInstanceOf(ResourceNotFoundException.class);

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

        assertThatThrownBy(() -> patientService.delete(7L)).isInstanceOf(ResourceNotFoundException.class);

        verify(patientRepository, never()).delete(any());
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
