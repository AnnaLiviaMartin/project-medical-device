import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import cv2
from PIL import Image
from torchvision import transforms, models
from sklearn.metrics import roc_curve, roc_auc_score
from matplotlib.patches import Patch
from nih_dataloader import create_dataloaders
from constants import IMAGENET_MEAN, IMAGENET_STD, PATHOLOGY_LIST, CONFIG, PIXEL
from nih_train import get_model

plt.rcParams.update({
    "font.family":    "sans-serif",
    "font.size":      11,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "figure.dpi":     150,
})

os.makedirs(CONFIG["plot_dir"], exist_ok=True)

# ==============================================================================
# HILFSFUNKTION: Modell + Daten laden
# ==============================================================================

def load_model_and_preds(config: dict):
    """
    Lädt das beste gespeicherte Modell und berechnet Vorhersagen
    auf dem Test-Set. Gibt rohe Wahrscheinlichkeiten und echte Labels zurück.

    Returns:
        model:      trainiertes nn.Module (im eval-Modus)
        all_probs:  np.array (N, 14) — Sigmoid-Wahrscheinlichkeiten
        all_labels: np.array (N, 14) — One-Hot-Labels
        device:     torch.device
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    _, _, test_loader, _ = create_dataloaders(
        data_dir=config["data_dir"],
        batch_size=config["batch_size"],
        num_workers=config["num_workers"],
    )

    model = get_model(num_classes=14).to(device)
    checkpoint = torch.load(
        os.path.join(config["output_dir"], "best_model.pt"),
        map_location=device,
        weights_only=False
    )
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    print(f"Modell geladen (Epoche {checkpoint['epoch']}, "
          f"Val-AUC {checkpoint['best_auc']:.4f})")

    filenames   = test_loader.dataset.df["Image Index"].tolist()
    image_index = test_loader.dataset.image_index  # dict: Dateiname -> echter Pfad

    all_probs, all_labels = [], []
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device, non_blocking=True)
            logits = model(images)
            probs  = torch.sigmoid(logits)
            all_probs.append(probs.cpu().numpy())
            all_labels.append(labels.numpy())

    all_probs  = np.concatenate(all_probs,  axis=0)  # (N, 14)
    all_labels = np.concatenate(all_labels, axis=0)  # (N, 14)

    return model, all_probs, all_labels, filenames, image_index, device


# ==============================================================================
# A) TRAININGSHISTORIE — Loss & AUC pro Epoche
# ==============================================================================

def plot_training_history(history: dict, save_path: str):
    """
    Zeigt Train/Val-Loss und Val-AUC über alle Epochen.

    `history` ist das Dict aus dem Training Loop:
      {
        "train_loss": [0.42, 0.38, ...],
        "val_loss":   [0.45, 0.40, ...],
        "val_auc":    [0.74, 0.78, ...],
      }
    """
    epochs = range(1, len(history["train_loss"]) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("Trainingshistorie", fontsize=14, fontweight="bold", y=1.02)

    # — Loss-Plot —
    ax1.plot(epochs, history["train_loss"], "o-",
             color="#2563eb", label="Train Loss", linewidth=2)
    ax1.plot(epochs, history["val_loss"],   "s--",
             color="#dc2626", label="Val Loss",   linewidth=2)
    ax1.set_xlabel("Epoche")
    ax1.set_ylabel("BCE Loss")
    ax1.set_title("Loss")
    ax1.legend()
    ax1.set_xticks(list(epochs))

    # Vertikale Linie an Stelle des Backbone-Unfreeze
    if len(epochs) >= 4:
        ax1.axvline(x=3.5, color="gray", linestyle=":", alpha=0.7)
        ax1.text(3.6, ax1.get_ylim()[1] * 0.95,
                 "Backbone\naufgetaut", fontsize=8, color="gray")

    # — AUC-Plot —
    ax2.plot(epochs, history["val_auc"], "D-",
             color="#16a34a", linewidth=2, markersize=7)
    ax2.set_xlabel("Epoche")
    ax2.set_ylabel("Macro ROC-AUC")
    ax2.set_title("Validation AUC")
    ax2.set_ylim(0.5, 1.0)
    ax2.set_xticks(list(epochs))
    ax2.axhline(y=0.8, color="gray", linestyle=":", alpha=0.6, label="Baseline ~0.80")
    ax2.legend(fontsize=9)

    # Bestes Ergebnis markieren
    best_epoch = int(np.argmax(history["val_auc"])) + 1
    best_auc   = max(history["val_auc"])
    ax2.annotate(f"Best: {best_auc:.4f}",
                 xy=(best_epoch, best_auc),
                 xytext=(best_epoch + 0.3, best_auc - 0.03),
                 arrowprops=dict(arrowstyle="->", color="#16a34a"),
                 fontsize=9, color="#16a34a")

    plt.tight_layout()
    path = save_path or os.path.join(CONFIG["plot_dir"], "training_history.png")
    plt.savefig(path, bbox_inches="tight")
    print(f"  Gespeichert: {path}")
    plt.show()


# ==============================================================================
# B) ROC-KURVEN — Eine Kurve pro Pathologie
# ==============================================================================

def plot_roc_curves(all_probs: np.ndarray,
                    all_labels: np.ndarray,
                    save_path: str):
    """
    Zeichnet alle 14 ROC-Kurven in einem 4x4-Grid.

    Jede Kurve zeigt den Trade-off zwischen True Positive Rate (Sensitivität)
    und False Positive Rate (1 - Spezifität). Je näher an der oberen linken
    Ecke, desto besser.
    AUC = 0.5 entspricht zufälligem Raten (graue Diagonale).
    """
    fig, axes = plt.subplots(4, 4, figsize=(16, 14))
    fig.suptitle("ROC-Kurven — NIH Chest X-ray (Test-Set)",
                 fontsize=15, fontweight="bold")

    colors = plt.cm.tab20(np.linspace(0, 1, 14))

    for i, (pathology, ax) in enumerate(zip(PATHOLOGY_LIST, axes.flat)):
        try:
            fpr, tpr, _ = roc_curve(all_labels[:, i], all_probs[:, i])
            auc = roc_auc_score(all_labels[:, i], all_probs[:, i])

            ax.plot(fpr, tpr, color=colors[i], linewidth=2,
                    label=f"AUC = {auc:.3f}")
            ax.fill_between(fpr, tpr, alpha=0.08, color=colors[i])

        except ValueError:
            ax.text(0.5, 0.5, "Keine pos.\nBeispiele",
                    ha="center", va="center", color="gray")

        # Diagonale (Zufall)
        ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, alpha=0.5)
        ax.set_title(pathology, fontsize=9, fontweight="bold")
        ax.set_xlabel("FPR", fontsize=7)
        ax.set_ylabel("TPR", fontsize=7)
        ax.legend(fontsize=8, loc="lower right")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)
        ax.tick_params(labelsize=7)

    # Letzten leeren Plot-Slot für Gesamt-Legende nutzen
    axes.flat[14].axis("off")
    axes.flat[15].axis("off")

    # Makro-AUC als Text im letzten Feld
    try:
        macro = np.mean([roc_auc_score(all_labels[:, i], all_probs[:, i]) for i in range(14)])
        axes.flat[14].text(0.5, 0.5,
                           f"Macro-AUC\n{macro:.4f}",
                           ha="center", va="center",
                           fontsize=16, fontweight="bold",
                           color="#1d4ed8",
                           transform=axes.flat[14].transAxes)
    except Exception:
        pass

    plt.tight_layout()
    path = save_path or os.path.join(CONFIG["plot_dir"], "roc_curves.png")
    plt.savefig(path, bbox_inches="tight")
    print(f"  Gespeichert: {path}")
    plt.show()


# ==============================================================================
# C) AUC-BALKENDIAGRAMM — Ranking aller 14 Pathologien
# ==============================================================================

def plot_auc_barchart(all_probs: np.ndarray,
                      all_labels: np.ndarray,
                      save_path: str):
    """
    Horizontales Balkendiagramm: AUC-Score aller 14 Pathologien,
    sortiert von hoch nach niedrig. Benchmarkwert aus dem CheXNet-Paper
    als Referenz eingeblendet.
    """
    auc_scores = {}
    for i, p in enumerate(PATHOLOGY_LIST):
        try:
            auc_scores[p] = roc_auc_score(all_labels[:, i], all_probs[:, i])
        except ValueError:
            auc_scores[p] = 0.0

    # Sortiert nach AUC (höchster oben)
    sorted_items = sorted(auc_scores.items(), key=lambda x: x[1])
    names  = [item[0] for item in sorted_items]
    scores = [item[1] for item in sorted_items]

    # Farben: grün wenn ≥ 0.80, gelb wenn 0.70–0.80, rot darunter
    bar_colors = ["#16a34a" if s >= 0.80 else
                  "#ca8a04" if s >= 0.70 else
                  "#dc2626"
                  for s in scores]

    fig, ax = plt.subplots(figsize=(9, 7))
    bars = ax.barh(names, scores, color=bar_colors, height=0.65, zorder=2)

    # Werte an den Balken
    for bar, score in zip(bars, scores):
        ax.text(score + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{score:.3f}", va="center", ha="left", fontsize=9)

    # Referenzlinie: CheXNet-Paper Durchschnitt (~0.841)
    ax.axvline(x=0.841, color="#7c3aed", linestyle="--",
               linewidth=1.5, label="CheXNet (Rajpurkar et al., 2017)")
    ax.axvline(x=np.mean(scores), color="#0891b2", linestyle="-.",
               linewidth=1.5, label=f"Unser Modell Ø {np.mean(scores):.3f}")

    ax.set_xlabel("ROC-AUC", fontsize=11)
    ax.set_title("AUC pro Pathologie — NIH Chest X-ray Test-Set",
                 fontsize=13, fontweight="bold")
    ax.set_xlim(0.5, 1.02)
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(axis="x", alpha=0.3, zorder=1)

    # Legende für Farbkodierung
    legend_elements = [
        Patch(facecolor="#16a34a", label="AUC ≥ 0.80"),
        Patch(facecolor="#ca8a04", label="AUC 0.70–0.80"),
        Patch(facecolor="#dc2626", label="AUC < 0.70"),
    ]
    ax.legend(handles=legend_elements + ax.get_legend_handles_labels()[0],
              fontsize=9, loc="lower right")

    plt.tight_layout()
    path = save_path or os.path.join(CONFIG["plot_dir"], "auc_barchart.png")
    plt.savefig(path, bbox_inches="tight")
    print(f"  Gespeichert: {path}")
    plt.show()


# ==============================================================================
# D) GRAD-CAM — Wo "schaut" das Modell hin?
# ==============================================================================

class GradCAM:
    """
    Gradient-weighted Class Activation Mapping für DenseNet-121.

    Wie es funktioniert:
      1. Forward Pass: Aktivierungen der letzten Conv-Schicht speichern
      2. Backward Pass: Gradienten der Ziel-Klasse bzgl. dieser Aktivierungen
      3. Global Average Pooling der Gradienten → Gewichte pro Feature-Map
      4. Gewichtete Summe der Aktivierungen → rohe Heatmap
      5. ReLU + Normalisierung + Hochskalierung auf Bildgröße

    Bei DenseNet-121 ist die letzte Conv-Schicht:
      model.features.denseblock4.denselayer16.conv2
    """

    def __init__(self, model: nn.Module):
        self.model = model
        self.model.eval()

        # Hooks für Aktivierungen und Gradienten
        self._activations = None
        self._gradients    = None

        # Ziel-Schicht: letzte Conv-Schicht von DenseBlock 4
        target_layer = model.features.denseblock4.denselayer16.conv2

        # Forward Hook: Aktivierungen speichern
        self._fwd_hook = target_layer.register_forward_hook(
            lambda module, input, output: setattr(self, "_activations", output)
        )
        # Backward Hook: Gradienten speichern
        self._bwd_hook = target_layer.register_full_backward_hook(
            lambda module, grad_in, grad_out: setattr(self, "_gradients", grad_out[0])
        )

    def __call__(self,
                 image_tensor: torch.Tensor,
                 class_idx: int,
                 device: torch.device) -> np.ndarray:
        """
        Berechnet die Grad-CAM-Heatmap für eine gegebene Klasse.

        Args:
            image_tensor: normalisiertes Bild
            class_idx:    Index der Ziel-Pathologie (0–13)
            device:       torch.device

        Returns:
            heatmap: Werte zwischen 0 und 1
        """
        image_tensor = image_tensor.to(device).requires_grad_(True)

        # Forward
        logits = self.model(image_tensor)           # (1, 14)
        score  = logits[0, class_idx]               # Skalar für Ziel-Klasse

        # Backward (nur für diese Klasse)
        self.model.zero_grad()
        score.backward()

        # Gradienten-Gewichte: Global Average Pooling über Raum
        # grads: (1, C, H, W) → weights: (C,)
        weights = self._gradients.mean(dim=(2, 3)).squeeze()  # (C,)

        # Aktivierungen: (1, C, H, W) → (C, H, W)
        activations = self._activations.squeeze()             # (C, H, W)

        # Gewichtete Summe: für jeden Kanal Aktivierung × Gewicht
        cam = torch.zeros(activations.shape[1:], device=device)
        for i, w in enumerate(weights):
            cam += w * activations[i]

        # ReLU: nur positive Einflüsse (negative würden andere Klassen aktivieren)
        cam = F.relu(cam)

        # Auf Bildgröße hochskalieren und normalisieren [0, 1]
        cam = cam.detach().cpu().numpy()
        cam = cv2.resize(cam, (PIXEL, PIXEL))
        if cam.max() > 0:
            cam = (cam - cam.min()) / (cam.max() - cam.min())

        return cam

    def remove_hooks(self):
        self._fwd_hook.remove()
        self._bwd_hook.remove()


def denormalize(tensor: torch.Tensor) -> np.ndarray:
    """Macht die ImageNet-Normalisierung rückgängig für die Visualisierung."""
    img  = tensor.squeeze().permute(1, 2, 0).numpy()
    img  = IMAGENET_STD * img + IMAGENET_MEAN
    img  = np.clip(img, 0, 1)
    return img


def plot_gradcam(model: nn.Module,
                 image_paths: list[str],
                 pathology_indices: list[int],
                 device: torch.device,
                 save_path: str):
    """
    Zeigt Originalbilder nebeneinander mit Grad-CAM-Overlay für
    eine oder mehrere Ziel-Pathologien.

    Args:
        model:             trainiertes DenseNet-121 (eval-Modus)
        image_paths:       Liste von Pfaden zu Röntgen-PNGs
        pathology_indices: Welche Pathologie(n) visualisieren (0–13)
        device:            torch.device

    Beispiel:
        plot_gradcam(
            model,
            image_paths=["./data/images/00000001_000.png"],
            pathology_indices=[2, 7],   # Effusion + Pneumothorax
            device=device,
        )
    """
    transform = transforms.Compose([
        transforms.Resize(PIXEL),
        transforms.CenterCrop(PIXEL),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    grad_cam = GradCAM(model)

    n_images = len(image_paths)
    n_classes = len(pathology_indices)
    # Spalten: Original + eine pro Pathologie
    n_cols = 1 + n_classes

    fig, axes = plt.subplots(n_images, n_cols,
                             figsize=(4 * n_cols, 4 * n_images))
    if n_images == 1:
        axes = axes[np.newaxis, :]  # Sicherstellen: immer 2D

    fig.suptitle("Grad-CAM — Was aktiviert das Modell?",
                 fontsize=14, fontweight="bold")

    for row, img_path in enumerate(image_paths):
        # Bild laden und vorbereiten
        pil_img    = Image.open(img_path).convert("RGB")
        img_tensor = transform(pil_img).unsqueeze(0)
        img_np     = denormalize(img_tensor)

        # Modell-Vorhersage für dieses Bild
        with torch.no_grad():
            logits = model(img_tensor.to(device))
            probs  = torch.sigmoid(logits).cpu().numpy()[0]  # (14,)

        # — Original-Bild —
        axes[row, 0].imshow(img_np, cmap="gray")
        axes[row, 0].set_title(
            os.path.basename(img_path),
            fontsize=8, fontweight="bold"
        )
        axes[row, 0].axis("off")

        # — Grad-CAM pro Pathologie —
        for col, cls_idx in enumerate(pathology_indices, start=1):
            heatmap = grad_cam(img_tensor.clone(), cls_idx, device)

            # Colormap auf Heatmap anwenden (Jet: blau→rot)
            heatmap_colored = cv2.applyColorMap(
                (heatmap * 255).astype(np.uint8), cv2.COLORMAP_JET
            )
            heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
            heatmap_colored = heatmap_colored / 255.0

            # Overlay: Original 60% + Heatmap 40%
            overlay = 0.6 * img_np + 0.4 * heatmap_colored
            overlay = np.clip(overlay, 0, 1)

            axes[row, col].imshow(overlay)
            pathology_name = PATHOLOGY_LIST[cls_idx]
            axes[row, col].set_title(
                f"{pathology_name}\np={probs[cls_idx]:.3f}",
                fontsize=8
            )
            axes[row, col].axis("off")

            # Farbskala-Leiste
            sm = plt.cm.ScalarMappable(cmap="jet",
                                        norm=plt.Normalize(vmin=0, vmax=1))
            plt.colorbar(sm, ax=axes[row, col], fraction=0.046, pad=0.04)

    grad_cam.remove_hooks()
    plt.tight_layout()
    path = save_path or os.path.join(CONFIG["plot_dir"], "gradcam.png")
    plt.savefig(path, bbox_inches="tight")
    print(f"  Gespeichert: {path}")
    plt.show()


def get_auc_per_class(all_probs: np.ndarray, all_labels: np.ndarray) -> dict:
    """AUC pro Pathologie — wird sowohl für den Barchart als auch für die
    automatische Grad-CAM-Klassenauswahl gebraucht."""
    scores = {}
    for i, p in enumerate(PATHOLOGY_LIST):
        try:
            scores[p] = roc_auc_score(all_labels[:, i], all_probs[:, i])
        except ValueError:
            scores[p] = float("nan")
    return scores

def select_gradcam_examples(
    all_probs: np.ndarray,
    all_labels: np.ndarray,
    filenames: list[str],
    image_index: dict,
    pathology_idx: int,
    n_per_group: int = 2,
) -> dict:
    """
    Wählt aussagekräftige Beispielbilder für eine Pathologie aus:
      - true_positives:  echte Positive mit HOHER Konfidenz
                          -> schaut das Modell auf die richtige Region?
      - false_positives: echte Negative mit HOHER Konfidenz
                          -> reagiert das Modell auf Artefakte
                             (Tubus, EKG-Elektroden, Beschriftung)?
      - false_negatives: echte Positive mit NIEDRIGER Konfidenz
                          -> was übersieht das Modell?

    Nutzt image_index (Dateiname -> echter Pfad), das test_loader.dataset
    bereits beim Aufbau per rglob() über ALLE images_XXX-Unterordner erstellt
    hat — keine eigene Annahme über die Ordnerstruktur nötig.

    Returns: dict mit Listen von vollständigen Bildpfaden je Gruppe
    """
    probs  = all_probs[:, pathology_idx]
    labels = all_labels[:, pathology_idx]

    pos_idx = np.where(labels == 1)[0]
    neg_idx = np.where(labels == 0)[0]

    tp_idx = pos_idx[np.argsort(-probs[pos_idx])][:n_per_group]   # höchste Prob unter Positiven
    fn_idx = pos_idx[np.argsort(probs[pos_idx])][:n_per_group]    # niedrigste Prob unter Positiven
    fp_idx = neg_idx[np.argsort(-probs[neg_idx])][:n_per_group]   # höchste Prob unter Negativen

    def to_paths(idx_array):
        return [image_index[filenames[i]] for i in idx_array if filenames[i] in image_index]

    return {
        "true_positives":  to_paths(tp_idx),
        "false_positives": to_paths(fp_idx),
        "false_negatives": to_paths(fn_idx),
    }


# ==============================================================================
# ALLES ZUSAMMEN AUSFÜHREN
# ==============================================================================

def visualise_all():
    print("=" * 60)
    print("  NIH Chest X-ray — Visualisierung")
    print("=" * 60)

    # --- Modell & Vorhersagen laden ---
    model, all_probs, all_labels, filenames, image_index, device = load_model_and_preds(CONFIG)

    # --- A) Trainingshistorie ---
    print("\n[A] Trainingshistorie...")
    history_path = os.path.join(CONFIG["output_dir"], "history.json")

    if os.path.exists(history_path):
        with open(history_path) as f:
            history = json.load(f)
        print(f"  Geladen: {history_path}")
        plot_training_history(history, "plots/training_history.png")
    else:
        print(f"  Warnung: '{history_path}' nicht gefunden.")
        print("  (Datei entsteht automatisch beim nächsten Trainingslauf.)")

    # --- B) ROC-Kurven ---
    print("\n[B] ROC-Kurven...")
    plot_roc_curves(all_probs, all_labels, "plots/roc_curves.png")

    # --- C) AUC-Balkendiagramm ---
    print("\n[C] AUC-Balkendiagramm...")
    plot_auc_barchart(all_probs, all_labels, "plots/auc_barchart.png")

    # --- D) Grad-CAM ---
    print("\n[D] Grad-CAM Heatmaps...")

    # Datengetriebene Auswahl: die N Pathologien mit der
    # SCHLECHTESTEN Test-AUC sind die naheliegendsten Kandidaten, um zu prüfen,
    # ob das Modell auf die falschen Bildregionen schaut.
    N_WORST = 3
    auc_scores = get_auc_per_class(all_probs, all_labels)
    worst_pathologies = sorted(auc_scores, key=lambda p: auc_scores[p])[:N_WORST]

    print(f"  Schwächste {N_WORST} Pathologien (niedrigste Test-AUC):")
    for p in worst_pathologies:
        print(f"    {p:<22} AUC={auc_scores[p]:.3f}")

    for pathology_name in worst_pathologies:
        pathology_idx = PATHOLOGY_LIST.index(pathology_name)

        examples = select_gradcam_examples(
            all_probs, all_labels, filenames, image_index,
            pathology_idx=pathology_idx, n_per_group=2,
        )

        for group_name, paths in examples.items():
            if not paths:
                print(f"  Keine Bilder für '{pathology_name}' / '{group_name}' gefunden.")
                continue
            print(f"  {pathology_name} / {group_name} ({len(paths)} Bilder)")
            plot_gradcam(
                model=model,
                image_paths=paths,
                pathology_indices=[pathology_idx],
                device=device,
                save_path=f"plots/gradcam_{pathology_name}_{group_name}.png",
            )

if __name__ == "__main__":
    visualise_all()