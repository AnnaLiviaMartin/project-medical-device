package de.hsrm.cs.master.medical.project.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.springframework.format.annotation.DateTimeFormat;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "patients")
@Getter
@Setter
public class Patient {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String firstName;

    @Column(nullable = false, length = 100)
    private String lastName;

    @Column(nullable = false)
    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate dateOfBirth;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private Sex sex;

    @Column(nullable = false, length = 255)
    private String diagnosis;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private PatientStatus status = PatientStatus.OUTPATIENT;

    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate lastVisit;

    @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
    private LocalDate nextAppointment;

    @Column(nullable = false)
    private String doctor;

    @Column(nullable = false)
    private String ward = "";

    // Adresse
    @Column(nullable = false)
    private String addressStreet = "";
    @Column(nullable = false)
    private String addressZip = "";
    @Column(nullable = false)
    private String addressCity = "";

    // Notfallkontakt
    @Column(nullable = false)
    private String emergencyContactName = "";
    @Column(nullable = false)
    private String emergencyContactRelation = "";
    @Column(nullable = false)
    private String emergencyContactPhone = "";

    // Versicherung
    @Column(nullable = false)
    private String insuranceProvider = "";
    @Column(nullable = false)
    private String insurancePolicyNumber = "";

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(nullable = false)
    private LocalDateTime updatedAt = LocalDateTime.now();

    @OneToMany(mappedBy = "patient", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<Allergy> allergies = new ArrayList<>();

    @OneToMany(mappedBy = "patient", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<Medication> medications = new ArrayList<>();

    @OneToMany(mappedBy = "patient", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private List<HistoryEntry> historyEntries = new ArrayList<>();

    @PreUpdate
    public void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    @Transient
    public String getFullName() {
        return firstName + " " + lastName;
    }

    public String getEmergencyContactInformation() {
        return emergencyContactName + " (" + emergencyContactRelation + ", " + emergencyContactPhone + ")";
    }

    public String getFullSearchInformation() {
        return getFullName() + " (" + this.id + " " + this.addressCity + " " + this.getEmergencyContactInformation() + ")";
    }

    @Transient
    public int getAge() {
        if (dateOfBirth == null) {
            return 0;
        }
        return Period.between(dateOfBirth, LocalDate.now()).getYears();
    }
}
