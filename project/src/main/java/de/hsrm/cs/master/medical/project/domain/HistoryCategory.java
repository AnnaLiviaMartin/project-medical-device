package de.hsrm.cs.master.medical.project.domain;

import lombok.Getter;

@Getter
public enum HistoryCategory {
    VISIT("Visit"),
    PROCEDURE("Procedure"),
    FINDING("Finding"),
    MEDICATION("Medication"),
    FOLLOW_UP("Follow-up");

    private final String label;

    HistoryCategory(String label) {
        this.label = label;
    }
}
