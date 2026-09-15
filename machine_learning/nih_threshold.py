"""
NIH Chest X-ray — Klassenspezifische Decision-Threshold-Optimierung
=====================================================================
AUC misst nur, wie gut das Modell Positive und Negative in eine RANGFOLGE
bringt — unabhängig von jedem konkreten Schwellenwert. Für eine praktische
Anwendung (Alarm ja/nein) braucht man aber irgendwann eine feste Schwelle,
ab der eine Wahrscheinlichkeit als "positiv" gilt. Bisher: pauschal 0.5.

Warum das problematisch ist:
    - Bei starkem Klassenungleichgewicht (z.B. Hernie: ~0.2% Prävalenz)
      liegen die meisten vorhergesagten Wahrscheinlichkeiten weit unter 0.5,
      selbst für tatsächlich positive Fälle. Ein fixer 0.5-Schwellenwert
      führt dann oft dazu, dass fast nie "positiv" vorhergesagt wird
      (hohe Spezifität, aber miserable Sensitivität).
    - Unterschiedliche Pathologien erfordern unterschiedliche Trade-offs

WICHTIG — Kein Data Leakage bei der Threshold-Wahl:
    Die Schwellenwerte werden ausschließlich auf dem VALIDATION-Set bestimmt.
    Das Test-Set wird nur benutzt, um die (fixen) Schwellenwerte am Ende
    EINMAL zu evaluieren. Würde man die Schwelle direkt auf dem Test-Set
    optimieren, wäre das dieselbe Art von Leakage wie beim Patienten-Split —
    die berichteten Kennzahlen wären zu optimistisch, weil man auf den
    Testdaten "getunt" hätte.
"""

import numpy as np
from sklearn.metrics import roc_curve, f1_score, confusion_matrix

from constants import PATHOLOGY_LIST


# ==============================================================================
# 1. SCHWELLENWERTE BESTIMMEN
# ==============================================================================

def find_optimal_thresholds(
    val_probs: np.ndarray,
    val_labels: np.ndarray,
    method: str = "youden",
) -> dict:
    """
    Bestimmt für jede der 14 Pathologien einen individuellen Decision-Threshold.

    Args:
        val_probs:  (N, 14) — Sigmoid-Wahrscheinlichkeiten auf dem VAL-Set
        val_labels: (N, 14) — echte Labels auf dem VAL-Set
        method:
            "youden" — maximiert Youden's J = Sensitivität + Spezifität - 1.
                       Guter, robuster Allzweck-Kompromiss zwischen beiden.
            "f1"     — maximiert den F1-Score. Reagiert stärker auf die
                       Klassenprävalenz, kann bei seltenen Klassen sinnvoller
                       sein als Youden.

    Returns:
        dict {pathology_name: optimal_threshold}
    """
    thresholds = {}

    for i, pathology in enumerate(PATHOLOGY_LIST): # pro Durchlauf aus (N, 14) eins Spalte nehmen
        y_true = val_labels[:, i] # 0/1 labels
        y_prob = val_probs[:, i] # vorhergesagte Wahrscheinlichkeiten

        if y_true.sum() == 0: # y_true.sum() = Anzahl der positiven Beispiele, wenn 0, dann gibt es keine positiven Beispiele
            # Keine positiven Beispiele im Val-Set für diese Klasse
            # -> Schwellenwert kann nicht sinnvoll bestimmt werden, Default behalten
            thresholds[pathology] = 0.5
            continue

        if method == "youden":
            fpr, tpr, roc_thresh = roc_curve(y_true, y_prob) # false positive rate, true positive rate, thresholds
            j_scores = tpr - fpr
            best_idx = int(np.argmax(j_scores)) # findet Index des besten Schwellenwertes, an dem am weitesten von der Zufalls-Diagonale entfernt ist
            thresholds[pathology] = float(roc_thresh[best_idx])

        elif method == "f1":
            candidate_thresholds = np.linspace(0.01, 0.99, 99) # festes Raster von 0.01 bis 0.99, um den besten Schwellenwert zu finden
            f1_scores = [
                f1_score(y_true, (y_prob >= t).astype(int), zero_division=0) # F1-Score berechnet(Wahrscheinlichkeiten bei genau diesem t in 0/1-Vorhersagen umgewandelt)
                for t in candidate_thresholds
            ] # Liste von 99 F1-Werten, quasi Brute-Force-Suche: alle 99 Kandidaten durchprobieren und besten nehmen
            best_idx = int(np.argmax(f1_scores))
            thresholds[pathology] = float(candidate_thresholds[best_idx])

        else:
            raise ValueError(f"Unbekannte Methode: '{method}'. Nutze 'youden' oder 'f1'.")

    return thresholds

# ==============================================================================
# 2. FESTE SCHWELLENWERTE AUF (TEST-)DATEN ANWENDEN UND BEWERTEN
# ==============================================================================

def evaluate_with_thresholds(
    probs: np.ndarray,
    labels: np.ndarray,
    thresholds: dict,
) -> dict:
    """
    Wendet die Schwellenwerte auf beliebige Daten an und berechnet pro Pathologie:
    Sensitivität (Recall), Spezifität, Precision und F1.

    Returns:
        dict {pathology_name: {"threshold", "sensitivity", "specificity", "precision", "f1"}}
    """
    results = {}

    for i, pathology in enumerate(PATHOLOGY_LIST):
        t = thresholds[pathology]
        y_true = labels[:, i] # 0/1 labels
        y_pred = (probs[:, i] >= t).astype(int) # Wahrscheinlichkeit, jede Wahrscheinlichkeit, die mind. t betraegt, wird True, sonst False

        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel() # alle 4 Werte erhaltbar durch eine Berechnung

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
        specificity = tn / (tn + fp) if (tn + fp) > 0 else float("nan")
        precision   = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
        f1 = (
            2 * precision * sensitivity / (precision + sensitivity)
            if (precision + sensitivity) > 0 and not np.isnan(precision + sensitivity)
            else float("nan")
        )

        results[pathology] = {
            "threshold":   t,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "precision":   precision,
            "f1":          f1,
        }

    return results

def print_threshold_report(results: dict, title: str = "Klassenspezifische Thresholds (Test-Set)"):
    print(f"\n=== {title} ===")
    print(f"{'Pathologie':<22} {'Schwelle':>9} {'Sens.':>7} {'Spez.':>7} {'Prec.':>7} {'F1':>7}")
    print("-" * 65)
    for pathology, r in results.items():
        print(
            f"{pathology:<22} {r['threshold']:>9.3f} "
            f"{r['sensitivity']:>7.3f} {r['specificity']:>7.3f} "
            f"{r['precision']:>7.3f} {r['f1']:>7.3f}"
        )
    print(
        "\nHinweis: Die Schwellenwerte wurden ausschließlich auf dem Validation-Set\n"
        "bestimmt und hier nur fix auf das Test-Set angewendet (kein Leakage)."
    )
