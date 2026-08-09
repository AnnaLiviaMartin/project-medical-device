package de.hsrm.cs.master.medical.project.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "medications")
@Getter
@Setter
public class Medication {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "patient_id", nullable = false)
    private Patient patient;

    @Column(nullable = false, length = 150)
    private String name;

    @Column(nullable = false, length = 50)
    private String dosage;

    @Column(nullable = false, length = 100)
    private String schedule;

    public Medication() {
    }

    public Medication(Patient patient, String name, String dosage, String schedule) {
        this.patient = patient;
        this.name = name;
        this.dosage = dosage;
        this.schedule = schedule;
    }
}
