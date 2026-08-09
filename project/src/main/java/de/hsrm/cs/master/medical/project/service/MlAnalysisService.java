package de.hsrm.cs.master.medical.project.service;

import de.hsrm.cs.master.medical.project.domain.MlAnalysisResult;

import java.nio.file.Path;

/**
 * Abstraktion ueber "fuehre die Roentgenbild-Analyse aus" - entspricht
 * ml.services.run_model_on_image() aus dem alten Django-Backend.
 *
 * WICHTIGER HINWEIS ZUR MIGRATION:
 * Das urspruengliche PyTorch/DenseNet-Modell samt Grad-CAM-Berechnung
 * (ml/services.py) laesst sich nicht 1:1 nach Java portieren - es basiert
 * auf torch/torchvision, die es fuer die JVM so nicht gibt. Fuer eine
 * echte Migration gibt es zwei sinnvolle Wege, die beide hinter genau
 * dieser Schnittstelle andockbar sind, ohne Controller/Service-Schicht
 * anzufassen:
 *
 *   1) RestMlAnalysisService: das trainierte Modell bleibt in Python,
 *      wird aber als eigener kleiner Inferenz-Microservice (z. B. FastAPI)
 *      betrieben; dieser Service hier ruft ihn per RestClient/WebClient auf.
 *   2) Modell per TorchScript/ONNX exportieren und ueber Deep Java Library
 *      (DJL, https://djl.ai) direkt in der JVM ausfuehren.
 *
 * Fuer dieses Grundgeruest ist stattdessen {@link SimulatedMlAnalysisService}
 * aktiv: sie erzeugt plausible, aber frei erfundene Wahrscheinlichkeiten
 * und ein illustratives Heatmap-Overlay, damit Upload -> Analyse -> Anzeige
 * End-to-End funktioniert und getestet werden kann. Die Ergebnisse sind
 * NICHT medizinisch verwertbar - das wird in der UI durchgaengig als
 * "Simulation" gekennzeichnet.
 */
public interface MlAnalysisService {
    MlAnalysisResult analyze(Path imagePath);
}
