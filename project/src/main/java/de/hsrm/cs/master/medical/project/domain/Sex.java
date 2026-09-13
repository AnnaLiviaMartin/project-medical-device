package de.hsrm.cs.master.medical.project.domain;

import lombok.Getter;

@Getter
public enum Sex {
    MALE("Male", "patients.gender.male"),
    FEMALE("Female", "patients.gender.female"),
    DIVERSE("Diverse", "patients.gender.nonbinary");

    private final String label;
    private final String messageKey;

    Sex(String label, String messageKey) {
        this.label = label;
        this.messageKey = messageKey;
    }

}
