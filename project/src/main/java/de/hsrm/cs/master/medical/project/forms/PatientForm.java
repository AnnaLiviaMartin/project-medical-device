package de.hsrm.cs.master.medical.project.forms;

import de.hsrm.cs.master.medical.project.domain.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Setter
@Getter
public class PatientForm {

    @NotBlank(message = "First name is required.")
    @Size(max = 100, message = "First name may be at most 100 characters long.")
    private String firstName = "";

    @NotBlank(message = "Last name is required.")
    @Size(max = 100, message = "Last name may be at most 100 characters long.")
    private String lastName = "";

    @NotNull(message = "Date of birth is required.")
    @Past(message = "Date of birth must be in the past.")
    private LocalDate dateOfBirth;

    @NotNull(message = "Please select a sex.")
    private Sex sex;

    @NotBlank(message = "Diagnosis is required.")
    @Size(max = 255, message = "Diagnosis may be at most 255 characters long.")
    private String diagnosis = "";

    @NotNull(message = "Please select a status.")
    private PatientStatus status = PatientStatus.OUTPATIENT;

    @NotNull(message = "Last visit date is required.")
    private LocalDate lastVisit;

    private LocalDate nextAppointment;

    @NotBlank(message = "Doctor is required.")
    @Size(max = 150, message = "Doctor may be at most 150 characters long.")
    private String doctor = "";

    @Size(max = 150, message = "Ward may be at most 150 characters long.")
    private String ward = "";

    @Size(max = 255)
    private String addressStreet = "";

    @Size(max = 20, message = "Postal code may be at most 20 characters long.")
    private String addressZip = "";

    @Size(max = 150)
    private String addressCity = "";

    @Size(max = 150)
    private String emergencyContactName = "";

    @Size(max = 100)
    private String emergencyContactRelation = "";

    @Pattern(regexp = "^$|^[0-9+()\\-\\s]{6,50}$", message = "Please enter a valid phone number.")
    private String emergencyContactPhone = "";

    @Size(max = 150)
    private String insuranceProvider = "";

    @Size(max = 100)
    private String insurancePolicyNumber = "";

    /** Freitext, ein Eintrag pro Zeile - wird im Service in einzelne Allergy-Entities zerlegt. */
    private String allergiesRaw = "";

    @Valid
    private List<MedicationForm> medications = new ArrayList<>();

    public void addEmptyMedicationRow() {
        medications.add(new MedicationForm());
    }

    /** Vom Nutzer tatsaechlich befuellte Allergien, getrimmt und ohne Leerzeilen. */
    public List<String> parsedAllergies() {
        if (allergiesRaw == null) {
            return List.of();
        }
        return allergiesRaw.lines()
                .map(String::trim)
                .filter(line -> !line.isEmpty())
                .collect(Collectors.toList());
    }

    /** Medikationszeilen ohne die vom "+ Add row"-Button erzeugten Leerzeilen. */
    public List<MedicationForm> nonEmptyMedications() {
        return medications.stream().filter(row -> !row.isBlank()).collect(Collectors.toList());
    }

    // --- cross-field check: naechster Termin darf nicht vor dem letzten Besuch liegen ---
    public boolean isNextAppointmentValid() {
        if (nextAppointment == null || lastVisit == null) {
            return true;
        }
        return !nextAppointment.isBefore(lastVisit);
    }

}
