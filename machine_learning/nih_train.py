import os
import time
import json
from typing import Dict, Tuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score
from torchvision import models

from constants import PATHOLOGY_LIST, CONFIG
from nih_dataloader import create_dataloaders
from nih_threshold import (
    evaluate_with_thresholds,
    find_optimal_thresholds,
    print_threshold_report,
)


# ==============================================================================
# 1. REPRODUZIERBARKEIT
# ==============================================================================


def set_seed(seed: int) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ==============================================================================
# 2. MODELL-ARCHITEKTUR
# ==============================================================================


def get_model(
    num_classes: int = 14,
    dropout: float = 0.25,
) -> nn.Module:
    """Erzeugt DenseNet-121 mit ImageNet-Gewichten und neuem Multi-Label-Head.

    Der Backbone wird zunächst eingefroren. In Phase 1 wird nur der neue
    Classifier trainiert. Ab `unfreeze_epoch` wird der Backbone im
    Trainingsloop mit kleinerer Lernrate mittrainiert.

    Hinweis: Kein Sigmoid im Modell. BCEWithLogitsLoss verarbeitet rohe
    Logits numerisch stabil; Sigmoid wird nur für AUC und Thresholds benutzt.
    """
    model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)

    for parameter in model.parameters():
        parameter.requires_grad = False

    num_features = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=dropout),
        nn.Linear(num_features, num_classes),
    )

    return model


# ==============================================================================
# 3. OPTIMIZER, LOSS UND SCHEDULER
# ==============================================================================
def freeze_batchnorm_stats(model: nn.Module) -> None:
    """
    Setzt BatchNorm-Layer im eingefrorenen Backbone auf eval().
    Dadurch werden ihre running_mean- und running_var-Statistiken
    in Phase 1 nicht mit kleinen Batches weiter verändert.
    """
    for module in model.features.modules():
        if isinstance(module, nn.modules.batchnorm._BatchNorm):
            module.eval()

def unfreeze_backbone(
    model: nn.Module,
    learning_rate: float,
    weight_decay: float,
) -> torch.optim.Optimizer:
    """Taut DenseNet-Backbone auf und erzeugt Optimizer mit zwei Lernraten."""
    for parameter in model.parameters():
        parameter.requires_grad = True

    optimizer = torch.optim.AdamW(
        [
            {
                "params": model.features.parameters(),
                "lr": learning_rate / 10,
            },
            {
                "params": model.classifier.parameters(),
                "lr": learning_rate,
            },
        ],
        weight_decay=weight_decay,
    )

    print("  Backbone aufgetaut — Fine-Tuning mit Differential Learning Rates.")
    print(
        f"  Backbone LR: {learning_rate / 10:.2e} | "
        f"Classifier LR: {learning_rate:.2e} | "
        f"Weight Decay: {weight_decay:.2e}"
    )
    return optimizer


def build_criterion(
    raw_pos_weights: torch.Tensor,
    config: dict,
    device: torch.device,
) -> nn.Module:
    """Erstellt BCEWithLogitsLoss mit konfigurierbarer pos_weight-Strategie.

    raw_pos_weights müssen vom DataLoader als `negative_count / positive_count`
    geliefert werden. Für einen sauberen Tuningvergleich wähle in CONFIG:
    - raw:  unveränderte Gewichte
    - sqrt: sqrt(neg / pos), weniger aggressiv für seltene Klassen
    - clip: Gewichte auf pos_weight_max begrenzen
    - none: keine Klassengewichte
    """
    mode = config.get("pos_weight_mode", "raw")

    if mode == "none":
        print("\nLoss: BCEWithLogitsLoss ohne pos_weight")
        return nn.BCEWithLogitsLoss()

    if mode == "sqrt":
        pos_weight = torch.sqrt(raw_pos_weights)
        print("\nLoss: BCEWithLogitsLoss mit sqrt(pos_weight)")
    elif mode == "clip":
        max_weight = float(config.get("pos_weight_max", 20.0))
        pos_weight = torch.clamp(raw_pos_weights, min=1.0, max=max_weight)
        print(
            "\nLoss: BCEWithLogitsLoss mit geclipptem pos_weight "
            f"(max={max_weight})"
        )
    elif mode == "raw":
        pos_weight = raw_pos_weights
        print("\nLoss: BCEWithLogitsLoss mit ursprünglichem pos_weight")
    else:
        raise ValueError(
            f"Unbekannter pos_weight_mode: {mode!r}. "
            "Erlaubt: raw, sqrt, clip, none."
        )

    pos_weight = pos_weight.to(device=device, dtype=torch.float32)

    print("Verwendete pos_weight-Werte:")
    for pathology, weight in zip(PATHOLOGY_LIST, pos_weight.detach().cpu().tolist()):
        print(f"  {pathology:<22} {weight:.3f}")

    return nn.BCEWithLogitsLoss(pos_weight=pos_weight)


def build_scheduler(
    optimizer: torch.optim.Optimizer,
) -> torch.optim.lr_scheduler.ReduceLROnPlateau:
    """Scheduler: reduziert LR, wenn sich die Validation-Macro-AUC nicht verbessert."""
    return torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode="max",
        factor=0.2,
        patience=2,
        threshold=0.001,
        threshold_mode="abs",
        min_lr=1e-7,
    )


# ==============================================================================
# 4. TRAINING UND VALIDIERUNG
# ==============================================================================


def train_one_epoch(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    epoch: int,
) -> float:
    model.train()

    # Phase 1: Backbone ist eingefroren.
    # BatchNorm-Statistiken im Backbone ebenfalls festhalten.
    if not any(parameter.requires_grad for parameter in model.features.parameters()):
        freeze_batchnorm_stats(model)

    total_loss = 0.0
    n_batches = len(loader)

    for batch_idx, (images, labels) in enumerate(loader):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True).float()

        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        if (batch_idx + 1) % 50 == 0:
            average_loss = total_loss / (batch_idx + 1)
            print(
                f"    Epoche {epoch} | Batch {batch_idx + 1}/{n_batches} | "
                f"Loss: {average_loss:.4f}"
            )

    return total_loss / n_batches


def validate(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float, Dict[str, float]]:
    """Berechnet Loss sowie ROC-AUC je Klasse und als Macro-Mittelwert."""
    model.eval()
    total_loss = 0.0
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True).float()

            logits = model(images)
            loss = criterion(logits, labels)
            total_loss += loss.item()

            probabilities = torch.sigmoid(logits)
            all_probs.append(probabilities.cpu().numpy())
            all_labels.append(labels.cpu().numpy())

    all_probs = np.concatenate(all_probs, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    auc_scores = {}
    for index, pathology in enumerate(PATHOLOGY_LIST):
        try:
            auc_scores[pathology] = roc_auc_score(
                all_labels[:, index],
                all_probs[:, index],
            )
        except ValueError:
            print(f"  Warnung: {pathology} hat im Split nicht beide Klassen.")

    if not auc_scores:
        raise RuntimeError("Keine AUC konnte berechnet werden.")

    macro_auc = float(np.mean(list(auc_scores.values())))
    average_loss = total_loss / len(loader)

    return average_loss, macro_auc, auc_scores


def get_probs_and_labels(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    device: torch.device,
) -> Tuple[np.ndarray, np.ndarray]:
    """Sammelt Sigmoid-Wahrscheinlichkeiten und Labels für einen kompletten Split."""
    model.eval()
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            logits = model(images)
            probabilities = torch.sigmoid(logits)

            all_probs.append(probabilities.cpu().numpy())
            all_labels.append(labels.cpu().numpy())

    return (
        np.concatenate(all_probs, axis=0),
        np.concatenate(all_labels, axis=0),
    )


# ==============================================================================
# 5. TRAININGSLOOP
# ==============================================================================


def train(config: dict) -> nn.Module:
    """Trainiert das Modell, speichert den besten Checkpoint und gibt ihn zurück."""
    os.makedirs(config["output_dir"], exist_ok=True)
    set_seed(config["random_seed"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n{'=' * 60}")
    print(f"  Device: {device}")
    if device.type == "cuda":
        print(f"  GPU:    {torch.cuda.get_device_name(0)}")
    print(f"{'=' * 60}\n")

    train_loader, val_loader, _, pos_weights = create_dataloaders(
        data_dir=config["data_dir"],
        batch_size=config["batch_size"],
        num_workers=config["num_workers"],
        random_seed=config["random_seed"],
    )

    images, labels = next(iter(train_loader))
    print("=== Batch-Inspektion für Training ===")
    print(f"  Bild-Shape:   {images.shape}")
    print(f"  Label-Shape:  {labels.shape}")
    print(f"  Raw pos_weights: {pos_weights}")

    model = get_model(
        num_classes=config["num_classes"],
        dropout=config.get("dropout", 0.25),
    ).to(device)

    criterion = build_criterion(
        raw_pos_weights=pos_weights,
        config=config,
        device=device,
    )

    optimizer = torch.optim.AdamW(
        filter(lambda parameter: parameter.requires_grad, model.parameters()),
        lr=config["learning_rate"],
        weight_decay=config["weight_decay"],
    )
    scheduler = build_scheduler(optimizer)

    best_auc = float("-inf")
    patience_counter = 0
    history = {
        "train_loss": [],
        "val_loss": [],
        "val_auc": [],
        "learning_rates": [],
    }
    checkpoint_path = os.path.join(config["output_dir"], "best_model.pt")
    unfreeze_epoch = int(config.get("unfreeze_epoch", 4))

    print(f"\nTraining gestartet: {config['num_epochs']} Epochen")
    print(f"Phase 1: nur Classifier bis einschließlich Epoche {unfreeze_epoch - 1}")
    print(f"Phase 2: Fine-Tuning ab Epoche {unfreeze_epoch}\n")

    for epoch in range(1, config["num_epochs"] + 1):
        started_at = time.time()

        if epoch == unfreeze_epoch:
            print("\n  → Wechsel zu Phase 2: Backbone wird aufgetaut.\n")
            optimizer = unfreeze_backbone(
                model=model,
                learning_rate=config["learning_rate"],
                weight_decay=config["weight_decay"],
            )
            scheduler = build_scheduler(optimizer)

        train_loss = train_one_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            criterion=criterion,
            device=device,
            epoch=epoch,
        )

        val_loss, macro_auc, auc_dict = validate(
            model=model,
            loader=val_loader,
            criterion=criterion,
            device=device,
        )

        scheduler.step(macro_auc)

        current_lrs = [group["lr"] for group in optimizer.param_groups]
        elapsed_seconds = time.time() - started_at

        history["train_loss"].append(float(train_loss))
        history["val_loss"].append(float(val_loss))
        history["val_auc"].append(float(macro_auc))
        history["learning_rates"].append(current_lrs)

        print(
            f"\nEpoche {epoch:02d}/{config['num_epochs']:02d} "
            f"({elapsed_seconds:.0f}s) | "
            f"Train Loss: {train_loss:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val AUC: {macro_auc:.4f} | "
            f"LR: {[f'{lr:.2e}' for lr in current_lrs]}"
        )

        print("  AUC pro Pathologie:")
        for name, auc in sorted(auc_dict.items(), key=lambda item: -item[1]):
            bar = "█" * int(auc * 20)
            print(f"    {name:<22} {auc:.4f}  {bar}")

        if macro_auc > best_auc:
            best_auc = macro_auc
            patience_counter = 0

            torch.save(
                {
                    "epoch": epoch,
                    "model_state": model.state_dict(),
                    "optim_state": optimizer.state_dict(),
                    "scheduler_state": scheduler.state_dict(),
                    "best_auc": best_auc,
                    "config": config,
                    "history": history,
                },
                checkpoint_path,
            )
            print(f"\n  ✓ Neues bestes Modell gespeichert (AUC: {best_auc:.4f})")
        else:
            patience_counter += 1
            print(
                f"\n  Kein Fortschritt "
                f"({patience_counter}/{config['patience']})"
            )

        if patience_counter >= config["patience"]:
            print(f"\n  Early Stopping nach Epoche {epoch}.")
            break

    history_path = os.path.join(config["output_dir"], "history.json")
    with open(history_path, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Training abgeschlossen. Beste Val-AUC: {best_auc:.4f}")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Trainingshistorie: {history_path}")
    print(f"{'=' * 60}")

    best_checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )
    model.load_state_dict(best_checkpoint["model_state"])
    model.eval()

    return model


# ==============================================================================
# 6. FINALER TEST
# ==============================================================================


def evaluate_on_test(config: dict) -> None:
    """Bewertet ausschließlich den besten Checkpoint auf dem bisher unberührten Testset."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint_path = os.path.join(config["output_dir"], "best_model.pt")

    _, val_loader, test_loader, pos_weights = create_dataloaders(
        data_dir=config["data_dir"],
        batch_size=config["batch_size"],
        num_workers=config["num_workers"],
        random_seed=config["random_seed"],
    )

    checkpoint = torch.load(
        checkpoint_path,
        map_location=device,
        weights_only=False,
    )

    checkpoint_config = checkpoint.get("config", config)
    model = get_model(
        num_classes=checkpoint_config["num_classes"],
        dropout=checkpoint_config.get("dropout", 0.25),
    ).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    print(
        f"Modell geladen (trainiert bis Epoche {checkpoint['epoch']}, "
        f"Val-AUC: {checkpoint['best_auc']:.4f})"
    )

    criterion = build_criterion(
        raw_pos_weights=pos_weights,
        config=checkpoint_config,
        device=device,
    )

    test_loss, macro_auc, auc_dict = validate(
        model=model,
        loader=test_loader,
        criterion=criterion,
        device=device,
    )

    print(f"\n{'=' * 60}")
    print("  TEST-ERGEBNISSE")
    print(f"{'=' * 60}")
    print(f"  Test Loss:    {test_loss:.4f}")
    print(f"  Macro AUC:    {macro_auc:.4f}")
    print("\n  AUC pro Pathologie:")
    for name, auc in sorted(auc_dict.items(), key=lambda item: -item[1]):
        bar = "█" * int(auc * 20)
        print(f"    {name:<22} {auc:.4f}  {bar}")

    val_probs, val_labels = get_probs_and_labels(model, val_loader, device)
    thresholds = find_optimal_thresholds(
        val_probs,
        val_labels,
        method="youden",
    )

    test_probs, test_labels = get_probs_and_labels(model, test_loader, device)
    threshold_results = evaluate_with_thresholds(
        test_probs,
        test_labels,
        thresholds,
    )
    print_threshold_report(threshold_results)


# ==============================================================================
# 7. ENTRY POINT
# ==============================================================================


if __name__ == "__main__":
    train(CONFIG)
    # Erst aktivieren, wenn das Tuning abgeschlossen ist und du das finale Modell
    # genau einmal auf dem unberührten Test-Set evaluieren möchtest:
    # evaluate_on_test(CONFIG)