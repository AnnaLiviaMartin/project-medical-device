package de.hsrm.cs.master.medical.project.forms;

import de.hsrm.cs.master.medical.project.domain.HistoryCategory;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.util.Set;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;

class HistoryEntryFormValidationTest {

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
        assertThat(validator.validate(validForm())).isEmpty();
    }

    @Test
    void missingDate_isRejected() {
        HistoryEntryForm form = validForm();
        form.setDate(null);

        assertThat(messagesFor(form, "date")).contains("{validation.history.date.notnull}");
    }

    @Test
    void blankTitle_isRejected() {
        HistoryEntryForm form = validForm();
        form.setTitle("   ");

        assertThat(messagesFor(form, "title")).contains("{validation.history.title.notblank}");
    }

    @Test
    void titleLongerThan255Characters_isRejected() {
        HistoryEntryForm form = validForm();
        form.setTitle("A".repeat(256));

        assertThat(messagesFor(form, "title")).contains("{validation.history.title.size}");
    }

    @Test
    void missingCategory_isRejected() {
        HistoryEntryForm form = validForm();
        form.setCategory(null);

        assertThat(messagesFor(form, "category")).contains("{validation.history.category.notnull}");
    }

    @Test
    void descriptionLongerThan4000Characters_isRejected() {
        HistoryEntryForm form = validForm();
        form.setDescription("A".repeat(4001));

        assertThat(messagesFor(form, "description")).contains("{validation.history.description.size}");
    }

    @Test
    void emptyDescriptionDoctorAndDepartment_areAccepted_becauseTheyAreOptional() {
        HistoryEntryForm form = validForm();
        form.setDescription("");
        form.setDoctor("");
        form.setDepartment("");

        assertThat(validator.validate(form)).isEmpty();
    }

    private Set<String> messagesFor(HistoryEntryForm form, String propertyPath) {
        return validator.validateProperty(form, propertyPath).stream()
                .map(ConstraintViolation::getMessage)
                .collect(Collectors.toSet());
    }

    private HistoryEntryForm validForm() {
        HistoryEntryForm form = new HistoryEntryForm();
        form.setDate(LocalDate.of(2026, 3, 1));
        form.setTitle("Follow-up Visit");
        form.setCategory(HistoryCategory.VISIT);
        form.setDescription("Routine check-up.");
        form.setDoctor("Dr. Klein");
        form.setDepartment("Cardiology");
        return form;
    }
}
