package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.MlAnalysisResult;

import java.nio.file.Path;

/**
 * Zwei Implementierungen stehen zur Wahl, umschaltbar per
 * "ml.analysis.provider" in application.properties:
 *
 *   - {@link SimulatedMlAnalysisService} ("simulated", Standard): erzeugt
 *     plausible, aber frei erfundene Wahrscheinlichkeiten und ein
 *     illustratives Heatmap-Overlay, damit Upload -> Analyse -> Anzeige
 *     End-to-End funktioniert, ohne dass ein ML-Service laufen muss. Die
 *     Ergebnisse sind NICHT medizinisch verwertbar - das wird in der UI
 *     durchgaengig als "Simulation" gekennzeichnet.
 *   - {@link RestMlAnalysisService} ("rest"): das trainierte Modell bleibt
 *     in Python, laeuft als eigener Inferenz-Microservice (FastAPI, siehe
 *     /ml-service) und wird von hier per RestClient aufgerufen. Nutzt
 *     denselben Code (Model-Loading, Grad-CAM per Forward-/Backward-Hooks)
 *     wie das urspruengliche Django-Backend.
 */
public interface MlAnalysisService {
    MlAnalysisResult analyze(Path imagePath);
}
