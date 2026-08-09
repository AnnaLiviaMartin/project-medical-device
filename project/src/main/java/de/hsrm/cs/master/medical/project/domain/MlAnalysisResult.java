package de.hsrm.cs.master.medical.project.domain;

import java.awt.image.BufferedImage;
import java.util.Map;

public record MlAnalysisResult(
        String label,
        double confidence,
        double threshold,
        Map<String, Double> scores,
        Map<String, BufferedImage> gradCamOverlaysByPathology
) {
}
