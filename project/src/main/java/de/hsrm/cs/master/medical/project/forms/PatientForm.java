package de.hsrm.cs.master.medical.project.forms;

import de.hsrm.cs.master.medical.project.domain.*;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.Setter;
import org.springframework.format.annotation.DateTimeFormat;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Setter
@Getter
public class PatientForm {

    @NotBlank(message = "{validation.patient.firstName.notblank}")
    @Size(max = 100, message = "{validation.patient.firstName.size}")
    private String firstName = "";

    @NotBlank(message = "{validation.patient.lastName.notblank}")
    @Size(max = 100, message = "{validation.patient.lastName.size}")
    private String lastName = "";

    @NotNull(message = "{validation.patient.dateOfBirth.notnull}")
    @Past(message = "{validation.patient.dateOfBirth.past}")
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate dateOfBirth;

    @NotNull(message = "{validation.patient.sex.notnull}")
    private Sex sex;

    @NotBlank(message = "{validation.patient.diagnosis.notblank}")
    @Size(max = 255, message = "{validation.patient.diagnosis.size}")
    private String diagnosis = "";

    @NotNull(message = "{validation.patient.status.notnull}")
    private PatientStatus status = PatientStatus.OUTPATIENT;

    @NotNull(message = "{validation.patient.lastVisit.notnull}")
    @Past(message = "{validation.patient.lastVisit.past}")
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate lastVisit;

    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate nextAppointment;

    @NotBlank(message = "{validation.patient.doctor.notblank}")
    @Size(max = 150, message = "{validation.patient.doctor.size}")
    private String doctor = "";

    @Size(max = 150, message = "{validation.patient.ward.size}")
    private String ward = "";

    @Size(max = 255, message = "{validation.history.address.size}")
    private String addressStreet = "";

    @Size(max = 20, message = "{validation.patient.addressZip.size}")
    private String addressZip = "";

    @Size(max = 150, message = "{validation.patient.addressCity.size}")
    private String addressCity = "";

    @Size(max = 150, message = "{validation.patient.emergencyContactName.size}")
    private String emergencyContactName = "";

    @Size(max = 100, message = "{validation.patient.emergencyContactRelation.size}")
    private String emergencyContactRelation = "";

    @Pattern(regexp = "^$|^[0-9+()\\-\\s]{6,50}$", message = "{validation.patient.emergencyContactPhone.pattern}")
    private String emergencyContactPhone = "";

    @Size(max = 150, message = "{validation.patient.insuranceProvider.size}")
    private String insuranceProvider = "";

    @Size(max = 100, message = "{validation.patient.insurancePolicyNumber.size}")
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
