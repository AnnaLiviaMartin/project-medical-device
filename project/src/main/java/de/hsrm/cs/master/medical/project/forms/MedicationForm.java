package de.hsrm.cs.master.medical.project.forms;

import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
public class MedicationForm {

    @Size(max = 150, message = "Medication name may be at most 150 characters long.")
    private String name = "";

    @Size(max = 50, message = "Dosage may be at most 50 characters long.")
    private String dosage = "";

    @Size(max = 100, message = "Schedule may be at most 100 characters long.")
    private String schedule = "";

    public boolean isBlank() {
        return isEmpty(name) && isEmpty(dosage) && isEmpty(schedule);
    }

    private boolean isEmpty(String value) {
        return value == null || value.trim().isEmpty();
    }

}
