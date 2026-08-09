package de.hsrm.cs.master.medical.project.domain;

import lombok.Getter;

@Getter
public enum Sex {
    MALE("Male"),
    FEMALE("Female"),
    DIVERSE("Diverse");

    private final String label;

    Sex(String label) {
        this.label = label;
    }

}
