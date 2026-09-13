package de.hsrm.cs.master.medical.project.domain;

import lombok.Getter;

@Getter
public enum PatientStatus {
    INPATIENT("Outpatient", "patients.list.filter.inpatient"),
    OUTPATIENT("Inpatient", "patients.list.filter.outpatient");

    private final String messageKey;
    private final String label;

    PatientStatus(String label, String messageKey) {
        this.label = label;
        this.messageKey = messageKey;
    }
}
