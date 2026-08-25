package de.hsrm.cs.master.medical.project.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "xray_images")
@Getter
@Setter
public class XRayImage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "study_id", nullable = false)
    private Study study;

    /** Relativer Pfad unterhalb des Upload-Verzeichnisses, z. B. "xray_images/uuid.png". */
    @Column(nullable = false)
    private String storedPath;

    @Column(nullable = false, updatable = false)
    private LocalDateTime uploadedAt = LocalDateTime.now();

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private PredictionStatus predictionStatus = PredictionStatus.PENDING;

    @OneToOne(mappedBy = "xrayImage", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    private Prediction prediction;
}
