import os
import numpy as np
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import multilabel_confusion_matrix

from constants import CONFIG, PATHOLOGY_LIST
from nih_dataloader import create_dataloaders
from nih_train import get_model, get_probs_and_labels
from nih_threshold import find_optimal_thresholds


def save_confusion_matrices(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    thresholds: np.ndarray,
    output_dir: str,
):
    """
    Erstellt für jede der 14 Pathologien eine eigene 2x2-Matrix:

                  Vorhergesagt
                Negativ   Positiv
    Tatsächlich
    Negativ        TN        FP
    Positiv        FN        TP
    """
    os.makedirs(output_dir, exist_ok=True)

    # thresholds: Array der Länge 14, jeweils ein Threshold pro Pathologie.
    y_pred = (y_prob >= thresholds).astype(int)

    # Für Multi-Label-Daten: eine 2x2-Matrix pro Klasse.
    matrices = multilabel_confusion_matrix(y_true, y_pred)

    fig, axes = plt.subplots(4, 4, figsize=(18, 18))
    axes = axes.flatten()

    for i, pathology in enumerate(PATHOLOGY_LIST):
        matrix = matrices[i]
        tn, fp, fn, tp = matrix.ravel()

        sns.heatmap(
            matrix,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            square=True,
            xticklabels=["Negativ", "Positiv"],
            yticklabels=["Negativ", "Positiv"],
            ax=axes[i],
        )

        axes[i].set_title(
            f"{pathology}\nTN={tn} | FP={fp} | FN={fn} | TP={tp}",
            fontsize=10,
        )
        axes[i].set_xlabel("Vorhergesagt")
        axes[i].set_ylabel("Tatsächlich")

    # 4x4-Grid enthält 16 Felder; bei 14 Klassen bleiben zwei leer.
    for i in range(len(PATHOLOGY_LIST), len(axes)):
        axes[i].axis("off")

    plt.suptitle(
        "Konfusionsmatrizen pro Pathologie — Test-Set",
        fontsize=16,
        fontweight="bold",
    )
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    output_path = os.path.join(output_dir, "confusion_matrices_test.png")
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"\nConfusion-Matrix gespeichert: {output_path}")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # Das Training wird nicht erneut ausgeführt.
    # Es werden nur Validation- und Testdaten für die Evaluation geladen.
    _, val_loader, test_loader, _ = create_dataloaders(
        data_dir=CONFIG["data_dir"],
        batch_size=CONFIG["batch_size"],
        num_workers=CONFIG["num_workers"],
        random_seed=CONFIG["random_seed"],
    )

    model = get_model(num_classes=CONFIG["num_classes"]).to(device)

    checkpoint_path = os.path.join(CONFIG["output_dir"], "best_model.pt")
    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )
    model.load_state_dict(checkpoint["model_state"])

    print(
        f"Checkpoint geladen: {checkpoint_path}\n"
        f"Beste Validation-AUC: {checkpoint['best_auc']:.4f}, "
        f"Epoche: {checkpoint['epoch']}"
    )

    # 1. Thresholds ausschließlich auf dem Validation-Set bestimmen.
    val_probs, val_labels = get_probs_and_labels(model, val_loader, device)

    threshold_dict = find_optimal_thresholds(
        val_probs,
        val_labels,
        method="youden",
    )

    # Das Dictionary wird exakt in die Reihenfolge von PATHOLOGY_LIST gebracht.
    thresholds = np.array(
        [threshold_dict[pathology] for pathology in PATHOLOGY_LIST],
        dtype=np.float32,
    )

    print("\nVerwendete Thresholds:")
    for pathology, threshold in zip(PATHOLOGY_LIST, thresholds):
        print(f"  {pathology:<22}: {threshold:.4f}")

    # 2. Testset mit fest eingefrorenen Validation-Thresholds auswerten.
    test_probs, test_labels = get_probs_and_labels(model, test_loader, device)

    save_confusion_matrices(
        y_true=test_labels,
        y_prob=test_probs,
        thresholds=thresholds,
        output_dir=CONFIG["plot_dir"],
    )


if __name__ == "__main__":
    main()