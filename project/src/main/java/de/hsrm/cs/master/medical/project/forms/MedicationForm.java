package de.hsrm.cs.master.medical.project.forms;

import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
public class MedicationForm {

    @Size(max = 150, message = "{validation.medication.name.size}")
    private String name = "";

    @Size(max = 50, message = "{validation.medication.dosage.size}")
    private String dosage = "";

    @Size(max = 100, message = "{validation.medication.schedule.size}")
    private String schedule = "";

    public boolean isBlank() {
        return isEmpty(name) && isEmpty(dosage) && isEmpty(schedule);
    }

    private boolean isEmpty(String value) {
        return value == null || value.trim().isEmpty();
    }

}
