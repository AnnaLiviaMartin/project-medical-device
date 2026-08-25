package de.hsrm.cs.master.medical.project.mapper;

import de.hsrm.cs.master.medical.project.domain.*;
import de.hsrm.cs.master.medical.project.forms.MedicationForm;
import de.hsrm.cs.master.medical.project.forms.PatientForm;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class PatientMapperTest {

    private PatientMapper mapper;

    @BeforeEach
    void setUp() {
        mapper = new PatientMapperImpl();
    }

    @Test
    void updatePatient_mapsPatientFields() {
        PatientForm form = validForm();
        Patient patient = new Patient();

        mapper.updatePatient(form, patient);

        assertThat(patient.getFirstName()).isEqualTo("Anna");
        assertThat(patient.getLastName()).isEqualTo("Becker");
        assertThat(patient.getDateOfBirth()).isEqualTo(LocalDate.of(1990, 1, 1));
        assertThat(patient.getSex()).isEqualTo(Sex.FEMALE);
        assertThat(patient.getDiagnosis()).isEqualTo("Hypertension");
        assertThat(patient.getStatus()).isEqualTo(PatientStatus.OUTPATIENT);
        assertThat(patient.getLastVisit()).isEqualTo(LocalDate.of(2026, 1, 1));
        assertThat(patient.getDoctor()).isEqualTo("Dr. Klein");
    }

    @Test
    void updatePatient_mapsAllergies() {
        PatientForm form = validForm();
        form.setAllergiesRaw("Penicillin\n  \nLatex\n");

        Patient patient = new Patient();

        mapper.updatePatient(form, patient);

        assertThat(patient.getAllergies()).extracting(Allergy::getName).containsExactly("Penicillin", "Latex");

        assertThat(patient.getAllergies()).allMatch(allergy -> allergy.getPatient() == patient);
    }

    @Test
    void updatePatient_mapsMedicationsAndTrimsValues() {
        PatientForm form = validForm();

        MedicationForm medication = new MedicationForm();
        medication.setName(" Metformin ");
        medication.setDosage(" 1000 mg ");
        medication.setSchedule(" 2x daily ");

        MedicationForm blankRow = new MedicationForm();

        form.setMedications(List.of(medication, blankRow));

        Patient patient = new Patient();

        mapper.updatePatient(form, patient);

        assertThat(patient.getMedications()).hasSize(1);

        Medication result = patient.getMedications().get(0);

        assertThat(result.getName()).isEqualTo("Metformin");
        assertThat(result.getDosage()).isEqualTo("1000 mg");
        assertThat(result.getSchedule()).isEqualTo("2x daily");
        assertThat(result.getPatient()).isSameAs(patient);
    }

    @Test
    void updatePatient_replacesExistingAllergiesAndMedications() {
        Patient patient = new Patient();

        patient.getAllergies().add(new Allergy(patient, "Old allergy"));

        patient.getMedications().add(new Medication(patient, "Old medication", "10 mg", "1x daily"));

        PatientForm form = validForm();
        form.setAllergiesRaw("Penicillin");

        MedicationForm medication = new MedicationForm();
        medication.setName("Metformin");
        medication.setDosage("1000 mg");
        medication.setSchedule("2x daily");

        form.setMedications(List.of(medication));

        mapper.updatePatient(form, patient);

        assertThat(patient.getAllergies()).extracting(Allergy::getName).containsExactly("Penicillin");

        assertThat(patient.getMedications()).extracting(Medication::getName).containsExactly("Metformin");
    }

    @Test
    void toForm_mapsPatientFields() {
        Patient patient = createPatient();

        PatientForm form = mapper.toForm(patient);

        assertThat(form.getFirstName()).isEqualTo("Anna");
        assertThat(form.getLastName()).isEqualTo("Becker");
        assertThat(form.getDateOfBirth()).isEqualTo(LocalDate.of(1990, 1, 1));
        assertThat(form.getSex()).isEqualTo(Sex.FEMALE);
        assertThat(form.getDiagnosis()).isEqualTo("Hypertension");
        assertThat(form.getStatus()).isEqualTo(PatientStatus.OUTPATIENT);
        assertThat(form.getLastVisit()).isEqualTo(LocalDate.of(2026, 1, 1));
        assertThat(form.getDoctor()).isEqualTo("Dr. Klein");
    }

    @Test
    void toForm_mapsAllergiesToAllergiesRaw() {
        Patient patient = createPatient();

        patient.getAllergies().add(new Allergy(patient, "Penicillin"));
        patient.getAllergies().add(new Allergy(patient, "Latex"));

        PatientForm form = mapper.toForm(patient);

        assertThat(form.getAllergiesRaw()).isEqualTo("Penicillin\nLatex");
    }

    @Test
    void toForm_mapsMedications() {
        Patient patient = createPatient();

        patient.getMedications().add(new Medication(patient, "Metformin", "1000 mg", "2x daily"));

        PatientForm form = mapper.toForm(patient);

        assertThat(form.getMedications()).hasSize(1);

        MedicationForm medication = form.getMedications().get(0);

        assertThat(medication.getName()).isEqualTo("Metformin");
        assertThat(medication.getDosage()).isEqualTo("1000 mg");
        assertThat(medication.getSchedule()).isEqualTo("2x daily");
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

    private Patient createPatient() {
        Patient patient = new Patient();

        patient.setId(1L);
        patient.setFirstName("Anna");
        patient.setLastName("Becker");
        patient.setDateOfBirth(LocalDate.of(1990, 1, 1));
        patient.setSex(Sex.FEMALE);
        patient.setDiagnosis("Hypertension");
        patient.setStatus(PatientStatus.OUTPATIENT);
        patient.setLastVisit(LocalDate.of(2026, 1, 1));
        patient.setDoctor("Dr. Klein");

        return patient;
    }
}