package de.hsrm.cs.master.medical.project.domain;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

@Getter
@Setter
@Entity
@Table(name = "predictions")
public class Prediction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "xray_image_id", nullable = false, unique = true)
    private XRayImage xrayImage;

    @Column(nullable = false, length = 100)
    private String label;

    @Column(nullable = false)
    private double confidence;

    @Column(nullable = false)
    private double threshold;

    /** Wahrscheinlichkeit je Pathologie (0.0 - 1.0), analog scores in Django. */
    @ElementCollection
    @CollectionTable(name = "prediction_scores", joinColumns = @JoinColumn(name = "prediction_id"))
    @MapKeyColumn(name = "pathology")
    @Column(name = "score")
    private Map<String, Double> scores = new LinkedHashMap<>();

    /** Relativer Pfad zum (simulierten) Grad-CAM-Overlay je positivem Befund. */
    @ElementCollection
    @CollectionTable(name = "prediction_gradcam_paths", joinColumns = @JoinColumn(name = "prediction_id"))
    @MapKeyColumn(name = "pathology")
    @Column(name = "path")
    private Map<String, String> gradCamPaths = new LinkedHashMap<>();

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @Transient
    public List<Map.Entry<String, Double>> getScoresSortedDescending() {
        return scores.entrySet().stream()
                .sorted((a, b) -> b.getValue().compareTo(a.getValue()))
                .collect(Collectors.toList());
    }
}
