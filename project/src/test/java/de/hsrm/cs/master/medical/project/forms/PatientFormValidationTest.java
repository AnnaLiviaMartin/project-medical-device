package de.hsrm.cs.master.medical.project.forms;

import de.hsrm.cs.master.medical.project.domain.PatientStatus;
import de.hsrm.cs.master.medical.project.domain.Sex;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.time.LocalDate;
import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;


class PatientFormValidationTest {

    private static ValidatorFactory validatorFactory;
    private static Validator validator;

    @BeforeAll
    static void setUpValidator() {
        validatorFactory = Validation.buildDefaultValidatorFactory();
        validator = validatorFactory.getValidator();
    }

    @AfterAll
    static void closeValidatorFactory() {
        validatorFactory.close();
    }

    @Test
    void fullyPopulatedForm_hasNoViolations() {
        PatientForm form = validForm();

        Set<ConstraintViolation<PatientForm>> violations = validator.validate(form);

        assertThat(violations).isEmpty();
    }

    @Test
    void blankFirstName_isRejected() {
        PatientForm form = validForm();
        form.setFirstName("  ");

        assertThat(messagesFor(form, "firstName")).contains("{validation.patient.firstName.notblank}");
    }

    @Test
    void firstNameLongerThan100Characters_isRejected() {
        PatientForm form = validForm();
        form.setFirstName("A".repeat(101));

        assertThat(messagesFor(form, "firstName")).contains("{validation.patient.firstName.size}");
    }

    @Test
    void blankLastName_isRejected() {
        PatientForm form = validForm();
        form.setLastName("");

        assertThat(messagesFor(form, "lastName")).contains("{validation.patient.lastName.notblank}");
    }

    @Test
    void missingDateOfBirth_isRejected() {
        PatientForm form = validForm();
        form.setDateOfBirth(null);

        assertThat(messagesFor(form, "dateOfBirth")).contains("{validation.patient.dateOfBirth.notnull}");
    }

    @Test
    void dateOfBirthInTheFuture_isRejected() {
        PatientForm form = validForm();
        form.setDateOfBirth(LocalDate.now().plusDays(1));

        assertThat(messagesFor(form, "dateOfBirth")).contains("{validation.patient.dateOfBirth.past}");
    }

    @Test
    void missingSex_isRejected() {
        PatientForm form = validForm();
        form.setSex(null);

        assertThat(messagesFor(form, "sex")).contains("{validation.patient.sex.notnull}");
    }

    @Test
    void blankDiagnosis_isRejected() {
        PatientForm form = validForm();
        form.setDiagnosis(" ");

        assertThat(messagesFor(form, "diagnosis")).contains("{validation.patient.diagnosis.notblank}");
    }

    @Test
    void missingStatus_isRejected() {
        PatientForm form = validForm();
        form.setStatus(null);

        assertThat(messagesFor(form, "status")).contains("{validation.patient.status.notnull}");
    }

    @Test
    void missingLastVisit_isRejected() {
        PatientForm form = validForm();
        form.setLastVisit(null);

        assertThat(messagesFor(form, "lastVisit")).contains("{validation.patient.lastVisit.notnull}");
    }

    @Test
    void blankDoctor_isRejected() {
        PatientForm form = validForm();
        form.setDoctor("");

        assertThat(messagesFor(form, "doctor")).contains("{validation.patient.doctor.notblank}");
    }

    @ParameterizedTest
    @ValueSource(strings = {"0176 12345678", "+49 176 1234567", "(030) 1234-5678"})
    void plausiblePhoneNumbers_areAccepted(String phone) {
        PatientForm form = validForm();
        form.setEmergencyContactPhone(phone);

        assertThat(messagesFor(form, "emergencyContactPhone")).isEmpty();
    }

    @Test
    void emptyPhoneNumber_isAccepted_becauseFieldIsOptional() {
        PatientForm form = validForm();
        form.setEmergencyContactPhone("");

        assertThat(messagesFor(form, "emergencyContactPhone")).isEmpty();
    }

    @ParameterizedTest
    @ValueSource(strings = {"not-a-number", "12345", "call-me-maybe"})
    void implausiblePhoneNumbers_areRejected(String phone) {
        PatientForm form = validForm();
        form.setEmergencyContactPhone(phone);

        assertThat(messagesFor(form, "emergencyContactPhone")).contains("{validation.patient.emergencyContactPhone.pattern}");
    }

    @Test
    void nextAppointmentBeforeLastVisit_isNotCaughtByBeanValidation_butByIsNextAppointmentValid() {
        // This particular rule is a cross-field check enforced manually in PatientController,
        // not via a jakarta.validation annotation - so Bean Validation alone lets it through...
        PatientForm form = validForm();
        form.setLastVisit(LocalDate.of(2026, 6, 1));
        form.setNextAppointment(LocalDate.of(2026, 5, 1));

        assertThat(validator.validate(form)).isEmpty();
        // ...which is exactly why PatientForm exposes this helper for the controller to call:
        assertThat(form.isNextAppointmentValid()).isFalse();
    }

    @Test
    void nextAppointmentOnOrAfterLastVisit_isValidAccordingToHelper() {
        PatientForm form = validForm();
        form.setLastVisit(LocalDate.of(2026, 6, 1));
        form.setNextAppointment(LocalDate.of(2026, 6, 1));

        assertThat(form.isNextAppointmentValid()).isTrue();
    }

    @Test
    void missingNextAppointment_isValidAccordingToHelper() {
        PatientForm form = validForm();
        form.setNextAppointment(null);

        assertThat(form.isNextAppointmentValid()).isTrue();
    }

    @Test
    void parsedAllergies_trimsWhitespaceAndDropsBlankLines() {
        PatientForm form = validForm();
        form.setAllergiesRaw("Penicillin\n \n  Latex  \n\nPollen");

        assertThat(form.parsedAllergies()).containsExactly("Penicillin", "Latex", "Pollen");
    }

    @Test
    void nonEmptyMedications_filtersOutBlankRows() {
        PatientForm form = validForm();
        MedicationForm filled = new MedicationForm();
        filled.setName("Metformin");
        MedicationForm blank = new MedicationForm();
        form.setMedications(java.util.List.of(filled, blank));

        assertThat(form.nonEmptyMedications()).containsExactly(filled);
    }

    private Set<String> messagesFor(PatientForm form, String propertyPath) {
        return validator.validateProperty(form, propertyPath).stream()
                .map(ConstraintViolation::getMessage)
                .collect(java.util.stream.Collectors.toSet());
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
