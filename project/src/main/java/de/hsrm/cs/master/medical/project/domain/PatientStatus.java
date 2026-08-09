package de.hsrm.cs.master.medical.project.domain;

import lombok.Getter;

@Getter
public enum PatientStatus {
    OUTPATIENT("Outpatient"),
    INPATIENT("Inpatient");

    private final String label;

    PatientStatus(String label) {
        this.label = label;
    }

}
