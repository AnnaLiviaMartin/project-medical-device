package de.hsrm.cs.master.medical.project.domain;

import lombok.Getter;

@Getter
public enum HistoryCategory {
    VISIT("Visit", "history.category.visit"),
    PROCEDURE("Procedure", "history.category.procedure"),
    FINDING("Finding", "history.category.finding"),
    MEDICATION("Medication", "history.category.medication"),
    FOLLOW_UP("Follow-up", "history.category.followup");

    private final String label;
    private final String messageKey;

    HistoryCategory(String label, String messageKey) {
        this.label = label;
        this.messageKey = messageKey;
    }
}
