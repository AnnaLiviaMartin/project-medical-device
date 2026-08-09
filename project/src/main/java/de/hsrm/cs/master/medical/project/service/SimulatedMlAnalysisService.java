package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.MlAnalysisResult;
import org.springframework.stereotype.Service;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * Platzhalter-Implementierung von {@link MlAnalysisService}, siehe
 * ausfuehrlichen Hinweis dort. Erzeugt deterministisch-plausible (per
 * Bild-Hash geseedete) Scores fuer die 14 NIH-ChestX-ray14-Pathologien
 * sowie ein illustratives, rot/blau eingefaerbtes Overlay fuer jeden
 * Befund oberhalb des Schwellwerts - rein visuell an das Grad-CAM-Overlay
 * aus dem Original angelehnt (rote Kanaele = hohe, blaue = niedrige
 * "Aktivierung"), aber ohne jeden Bezug zu echten Modell-Gradienten.
 */
@Service
public class SimulatedMlAnalysisService implements MlAnalysisService {

    /** Klassen des NIH ChestX-ray14 Datensatzes, siehe machine_learning/constants.py im Ursprungsprojekt. */
    // TODO enums
    // TODO ersetzen mit echter Analyse
    private static final List<String> PATHOLOGIES = List.of(
            "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass",
            "Nodule", "Pneumonia", "Pneumothorax", "Consolidation", "Edema",
            "Emphysema", "Fibrosis", "Pleural Thickening", "Hernia"
    );

    private static final double THRESHOLD = 0.5;
    private static final int OVERLAY_SIZE = 320;

    @Override
    public MlAnalysisResult analyze(Path imagePath) {
        long seed = seedFrom(imagePath);
        Random random = new Random(seed);

        Map<String, Double> scores = generateScores(random);

        String bestPathology = scores.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("No Finding");
        double bestConfidence = scores.getOrDefault(bestPathology, 0.0);
        String label = bestConfidence >= THRESHOLD ? bestPathology : "No Finding";

        BufferedImage baseImage = readAsRgb(imagePath);

        Map<String, BufferedImage> overlays = new LinkedHashMap<>();
        for (Map.Entry<String, Double> entry : scores.entrySet()) {
            if (entry.getValue() >= THRESHOLD) {
                overlays.put(entry.getKey(), renderSyntheticHeatmap(baseImage, seed, entry.getKey()));
            }
        }

        return new MlAnalysisResult(label, bestConfidence, THRESHOLD, scores, overlays);
    }

    private long seedFrom(Path imagePath) {
        try {
            byte[] bytes = Files.readAllBytes(imagePath);
            long hash = 1125899906842597L;
            // Nur jedes 97. Byte einbeziehen: grosse Roentgenbilder muessen fuer
            // einen stabilen Seed nicht vollstaendig durchlaufen werden.
            for (int i = 0; i < bytes.length; i += 97) {
                hash = 31 * hash + bytes[i];
            }
            return hash;
        } catch (IOException e) {
            return imagePath.toString().hashCode();
        }
    }

    private Map<String, Double> generateScores(Random random) {
        double roll = random.nextDouble();
        int numPositive;
        if (roll < 0.40) numPositive = 0;
        else if (roll < 0.75) numPositive = 1;
        else if (roll < 0.93) numPositive = 2;
        else numPositive = 3;

        List<String> shuffled = new java.util.ArrayList<>(PATHOLOGIES);
        java.util.Collections.shuffle(shuffled, random);

        Map<String, Double> scores = new LinkedHashMap<>();
        for (int i = 0; i < shuffled.size(); i++) {
            String pathology = shuffled.get(i);
            double score;
            if (i < numPositive) {
                score = 0.55 + random.nextDouble() * 0.40; // 0.55 - 0.95
            } else {
                score = 0.02 + random.nextDouble() * 0.40; // 0.02 - 0.42
            }
            scores.put(pathology, Math.round(score * 10000.0) / 10000.0);
        }
        // stabile, fachlich sinnvolle Reihenfolge statt Shuffle-Reihenfolge
        Map<String, Double> ordered = new LinkedHashMap<>();
        for (String pathology : PATHOLOGIES) {
            ordered.put(pathology, scores.get(pathology));
        }
        return ordered;
    }

    private BufferedImage readAsRgb(Path imagePath) {
        try {
            BufferedImage image = ImageIO.read(imagePath.toFile());
            if (image == null) {
                return placeholderImage();
            }
            BufferedImage rgb = new BufferedImage(image.getWidth(), image.getHeight(), BufferedImage.TYPE_INT_RGB);
            Graphics2D g = rgb.createGraphics();
            g.drawImage(image, 0, 0, Color.BLACK, null);
            g.dispose();
            return rgb;
        } catch (IOException e) {
            return placeholderImage();
        }
    }

    private BufferedImage placeholderImage() {
        BufferedImage image = new BufferedImage(OVERLAY_SIZE, OVERLAY_SIZE, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = image.createGraphics();
        g.setColor(new Color(30, 30, 30));
        g.fillRect(0, 0, OVERLAY_SIZE, OVERLAY_SIZE);
        g.dispose();
        return image;
    }

    /**
     * Zeichnet einen halbtransparenten roten "Aktivierungsfleck" auf eine
     * abgedunkelte Graustufen-Kopie des Originalbilds - optisch angelehnt an
     * ein Grad-CAM-Overlay, aber komplett synthetisch und ohne jede
     * Verbindung zu echten Modellgewichten.
     */
    private BufferedImage renderSyntheticHeatmap(BufferedImage base, long seed, String pathology) {
        int size = Math.min(OVERLAY_SIZE, Math.max(base.getWidth(), base.getHeight()));
        BufferedImage scaledBase = scale(base, size, size);

        BufferedImage overlay = new BufferedImage(size, size, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = overlay.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Graustufen-Basis abgedunkelt zeichnen
        g.drawImage(scaledBase, 0, 0, null);
        g.setColor(new Color(0, 0, 0, 90));
        g.fillRect(0, 0, size, size);

        Random random = new Random(seed + pathology.hashCode());
        int blobCount = 1 + random.nextInt(2);
        for (int i = 0; i < blobCount; i++) {
            float cx = size * (0.3f + random.nextFloat() * 0.4f);
            float cy = size * (0.3f + random.nextFloat() * 0.4f);
            float radius = size * (0.18f + random.nextFloat() * 0.15f);

            RadialGradientPaint paint = new RadialGradientPaint(
                    new Point2D_Float(cx, cy),
                    radius,
                    new float[]{0f, 0.6f, 1f},
                    new Color[]{
                            new Color(255, 40, 20, 200),
                            new Color(255, 140, 0, 120),
                            new Color(20, 60, 200, 0)
                    }
            );
            g.setPaint(paint);
            g.fillOval((int) (cx - radius), (int) (cy - radius), (int) (radius * 2), (int) (radius * 2));
        }
        g.dispose();
        return overlay;
    }

    private BufferedImage scale(BufferedImage source, int width, int height) {
        BufferedImage scaled = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        Graphics2D g = scaled.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        g.drawImage(source, 0, 0, width, height, null);
        g.dispose();
        return scaled;
    }

    /** Kleiner lokaler Alias, um keinen zusaetzlichen Import-Konflikt mit java.awt.Point zu erzeugen. */
    private static class Point2D_Float extends java.awt.geom.Point2D.Float {
        Point2D_Float(float x, float y) {
            super(x, y);
        }
    }
}
