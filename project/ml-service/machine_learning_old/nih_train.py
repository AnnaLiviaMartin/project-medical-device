import os
import time
import numpy as np
import torch
import json
import torch.nn as nn
from torchvision import models
from sklearn.metrics import roc_auc_score

from nih_dataloader import create_dataloaders
from nih_threshold import find_optimal_thresholds, evaluate_with_thresholds, print_threshold_report
from constants import PATHOLOGY_LIST, CONFIG

# ==============================================================================
# 1. MODELL-ARCHITEKTUR
# ==============================================================================

def get_model(num_classes: int = 14) -> nn.Module:
    """
    DenseNet-121 mit vortrainierten ImageNet-Gewichten.

    Was hier passiert:
      - Alle Convolution-Schichten bleiben eingefroren (Feature Extractor)
      - Nur der neue Classifier wird von Grund auf trainiert
      - Kein Sigmoid, BCEWithLogitsLoss macht das intern stabiler.
    """
    model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)

    # --- Strategie: Zweiphasiges Training ---
    # Phase 1 (erste Epochen): Nur den Classifier trainieren
    #   → Backbone einfrieren, damit die vortrainierten Gewichte nicht
    #     sofort überschrieben werden ("Feature Extraction")
    for param in model.parameters():
        param.requires_grad = False

    # Letzten Classifier-Layer ersetzen und trainierbar machen
    num_features = model.classifier.in_features  # = 1024 bei DenseNet-121
    model.classifier = nn.Sequential(
        nn.Linear(num_features, num_classes),
        # KEIN Sigmoid hier — BCEWithLogitsLoss ist numerisch stabiler
    )

    return model


def unfreeze_backbone(model: nn.Module, learning_rate: float) -> torch.optim.Optimizer:
    """
    Phase 2: Backbone auftauen und mit kleinerer Lernrate fine-tunen.

    Typischer Zeitpunkt: nach ~3-5 Epochen, wenn der Classifier konvergiert hat.
    Der Backbone bekommt eine 10x kleinere Lernrate als der Classifier,
    um die vortrainierten Gewichte sanft anzupassen (Differential Learning Rates).
    """
    for param in model.parameters():
        param.requires_grad = True

    # Differential Learning Rates: Backbone viel kleiner als Classifier
    optimizer = torch.optim.AdamW([
        {"params": model.features.parameters(), "lr": learning_rate / 10},
        {"params": model.classifier.parameters(), "lr": learning_rate},
    ], weight_decay=1e-5)

    print("  Backbone aufgetaut — Fine-Tuning mit Differential Learning Rates.")
    print(f"  Backbone LR: {learning_rate/10:.2e} | Classifier LR: {learning_rate:.2e}")
    return optimizer


# ==============================================================================
# 2. EINE TRAININGS-EPOCHE
# ==============================================================================

def train_one_epoch(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    epoch: int,
) -> float:
    """
    Führt eine komplette Trainings-Epoche durch.
    Gibt den durchschnittlichen Loss der Epoche zurück.
    """
    model.train()
    total_loss = 0.0
    n_batches = len(loader)

    for batch_idx, (images, labels) in enumerate(loader):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        # Forward Pass
        optimizer.zero_grad()
        logits = model(images)           # Shape: (batch, 14) — rohe Logits
        loss = criterion(logits, labels) # BCEWithLogitsLoss intern: sigmoid(logits)

        # Backward Pass
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        # Fortschritt anzeigen (alle 50 Batches)
        if (batch_idx + 1) % 50 == 0:
            avg = total_loss / (batch_idx + 1)
            print(f"    Epoche {epoch} | Batch {batch_idx+1}/{n_batches} | Loss: {avg:.4f}")

    return total_loss / n_batches


# ==============================================================================
# 3. VALIDIERUNGS-EPOCHE MIT ROC-AUC
# ==============================================================================

def validate(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
):
    """
    Bewertet das Modell auf dem Validierungsset.

    Gibt zurück:
      - val_loss:   Durchschnittlicher Loss
      - macro_auc:  Durchschnittlicher ROC-AUC über alle 14 Klassen
      - auc_dict:   ROC-AUC pro Pathologie (für detaillierte Analyse)

    Warum ROC-AUC und nicht Accuracy?
      Bei starkem Klassenungleichgewicht (Hernie: ~0.2%) wäre ein Modell,
      das immer "negativ" vorhersagt, 99.8% akkurat — aber nutzlos.
      ROC-AUC misst, wie gut das Modell die Klassen TRENNEN kann,
      unabhängig von der Häufigkeit.
    """
    model.eval()
    total_loss = 0.0

    # Vorhersagen und echte Labels sammeln
    all_logits  = []   # rohe Modell-Ausgaben
    all_labels  = []   # echte Labels

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            logits = model(images)
            loss = criterion(logits, labels)
            total_loss += loss.item()

            # Sigmoid für Wahrscheinlichkeiten (nur für AUC, nicht für Loss)
            probs = torch.sigmoid(logits)
            all_logits.append(probs.cpu().numpy())
            all_labels.append(labels.cpu().numpy())

    # Arrays zusammenführen: Shape (N_gesamt, 14)
    all_logits = np.concatenate(all_logits, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    # ROC-AUC pro Klasse berechnen
    auc_scores = {}
    for i, pathology in enumerate(PATHOLOGY_LIST):
        try:
            auc = roc_auc_score(all_labels[:, i], all_logits[:, i])
            auc_scores[pathology] = auc
        except ValueError:
            # Kann passieren wenn eine Klasse im Val-Set gar nicht vorkommt
            print(f"  Warnung: {pathology} hat keine positiven Beispiele im Val-Set.")

    macro_auc = np.mean(list(auc_scores.values()))
    val_loss  = total_loss / len(loader)

    return val_loss, macro_auc, auc_scores


def get_probs_and_labels(
    model: nn.Module,
    loader: torch.utils.data.DataLoader,
    device: torch.device,
):
    """
    Sammelt rohe Sigmoid-Wahrscheinlichkeiten und Labels für einen
    kompletten Loader. Wird für die Threshold-Optimierung gebraucht.
    Returns:
        all_probs:  (N, 14) np.ndarray
        all_labels: (N, 14) np.ndarray
    """
    model.eval()
    all_probs, all_labels = [], []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            logits = model(images)
            probs  = torch.sigmoid(logits)
            all_probs.append(probs.cpu().numpy())
            all_labels.append(labels.numpy())

    return np.concatenate(all_probs, axis=0), np.concatenate(all_labels, axis=0)


# ==============================================================================
# 4. TRAINING LOOP
# ==============================================================================

def train(config: dict) -> nn.Module:
    """
    Kompletter Training Loop mit:
      - Zweiphasigem Training (Freeze → Unfreeze)
      - Early Stopping
      - Best-Model-Checkpointing
    """
    os.makedirs(config["output_dir"], exist_ok=True)
    torch.manual_seed(config["random_seed"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n{'='*60}")
    print(f"  Device: {device}")
    if device.type == "cuda":
        print(f"  GPU:    {torch.cuda.get_device_name(0)}")
    print(f"{'='*60}\n")

    train_loader, val_loader, _, pos_weights = create_dataloaders(
        data_dir=config["data_dir"],
        batch_size=config["batch_size"],
        num_workers=config["num_workers"],
        random_seed=config["random_seed"],
    )

    images, labels = next(iter(train_loader))
    print(f"\n=== Batch-Inspektion für Training ===")
    print(f"  Bild-Shape:   {images.shape}")
    print(f"  Label-Shape:  {labels.shape}")
    print(f"  pos_weights:  {pos_weights}")    # → Tensor der Länge 14

    model = get_model(num_classes=config["num_classes"]).to(device)

    # --- Loss: BCEWithLogitsLoss mit Class Weights (numerisch sauberer wie Sigmoid-Aktivierung) ---
    criterion = nn.BCEWithLogitsLoss(
        pos_weight=pos_weights.to(device)
    )

    # --- Phase 1 Optimizer: nur Classifier-Parameter ---
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=config["learning_rate"],
        weight_decay=config["weight_decay"],
    )

    # Learning Rate Scheduler: reduziert LR wenn Val-AUC nicht besser wird
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="max", factor=0.5, patience=2
    )

    # --- Tracking ---
    best_auc = 0.0
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "val_auc": []}

    print(f"Training gestartet: {config['num_epochs']} Epochen\n")

    for epoch in range(1, config["num_epochs"] + 1):
        t0 = time.time()

        # Nach Epoche 3: Backbone auftauen (zweiphasiges Training)
        if epoch == 4:
            print("\n  → Wechsel zu Phase 2: Backbone wird aufgetaut.\n")
            optimizer = unfreeze_backbone(model, config["learning_rate"])
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode="max", factor=0.5, patience=2
            )

        # Training
        train_loss = train_one_epoch(
            model, train_loader, optimizer, criterion, device, epoch
        )

        # Validierung
        val_loss, macro_auc, auc_dict = validate(
            model, val_loader, criterion, device
        )

        # LR-Scheduler updaten (basierend auf Val-AUC)
        scheduler.step(macro_auc)

        # Ergebnisse loggen
        elapsed = time.time() - t0
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_auc"].append(macro_auc)

        print(f"\nEpoche {epoch:02d}/{config['num_epochs']:02d} "
              f"({elapsed:.0f}s) | "
              f"Train Loss: {train_loss:.4f} | "
              f"Val Loss: {val_loss:.4f} | "
              f"Val AUC: {macro_auc:.4f}")

        # Detaillierte AUC-Tabelle ausgeben
        print("  AUC pro Pathologie:")
        for name, auc in sorted(auc_dict.items(), key=lambda x: -x[1]):
            bar = "█" * int(auc * 20)
            print(f"    {name:<22} {auc:.4f}  {bar}")

        # Best Model speichern
        if macro_auc > best_auc:
            best_auc = macro_auc
            patience_counter = 0
            checkpoint_path = os.path.join(
                config["output_dir"], "best_model.pt"
            )
            torch.save({
                "epoch":       epoch,
                "model_state": model.state_dict(),
                "optim_state": optimizer.state_dict(),
                "best_auc":    best_auc,
                "config":      config,
            }, checkpoint_path)
            print(f"\n  ✓ Neues bestes Modell gespeichert (AUC: {best_auc:.4f})")
        else:
            patience_counter += 1
            print(f"\n  Kein Fortschritt ({patience_counter}/{config['patience']})")

        if patience_counter >= config["patience"]:
            print(f"\n  Early Stopping nach Epoche {epoch}.")
            break

    print(f"\n{'='*60}")
    print(f"Training abgeschlossen. Bestes Val-AUC: {best_auc:.4f}")
    print(f"Checkpoint: {os.path.join(config['output_dir'], 'best_model.pt')}")
    print(f"{'='*60}")

    # Speichere Trainingshistorie als JSON für spätere Visualisierung
    history_path = os.path.join(config["output_dir"], "history.json")
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    print(f"Trainingshistorie gespeichert: {history_path}")

    return model


# ==============================================================================
# 5. FINALER TEST auf dem Test-Set
# ==============================================================================

def evaluate_on_test(config: dict):
    """
    Lädt das beste gespeicherte Modell und evaluiert es auf dem Test-Set.
    Nur einmal am Ende aufrufen — nicht während des Trainings!
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Val-Loader wird jetzt zusätzlich gebraucht: die Decision-Thresholds
    # werden AUSSCHLIESSLICH auf dem Val-Set bestimmt, niemals auf dem Test-Set
    # (sonst Data Leakage bei der Threshold-Wahl).
    _, val_loader, test_loader, pos_weights = create_dataloaders(
        data_dir=config["data_dir"],
        batch_size=config["batch_size"],
        num_workers=config["num_workers"],
    )
    model = get_model(num_classes=config["num_classes"]).to(device)
    checkpoint = torch.load(
        os.path.join(config["output_dir"], "best_model.pt"),
        map_location=device,
        weights_only=False
    )
    model.load_state_dict(checkpoint["model_state"])
    print(f"Modell geladen (trainiert bis Epoche {checkpoint['epoch']}, "
          f"Val-AUC: {checkpoint['best_auc']:.4f})")

    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weights.to(device))
    test_loss, macro_auc, auc_dict = validate(model, test_loader, criterion, device)

    print(f"\n{'='*60}")
    print(f"  TEST-ERGEBNISSE")
    print(f"{'='*60}")
    print(f"  Test Loss:    {test_loss:.4f}")
    print(f"  Macro AUC:    {macro_auc:.4f}")
    print(f"\n  AUC pro Pathologie:")
    for name, auc in sorted(auc_dict.items(), key=lambda x: -x[1]):
        bar = "█" * int(auc * 20)
        print(f"    {name:<22} {auc:.4f}  {bar}")

    # ==========================================================================
    # Klassenspezifische Decision-Thresholds statt pauschal 0.5
    # ==========================================================================
    # Schritt 1: Schwellenwerte NUR auf dem Val-Set bestimmen
    val_probs, val_labels = get_probs_and_labels(model, val_loader, device)
    thresholds = find_optimal_thresholds(val_probs, val_labels, method="youden")

    # Schritt 2: Diese (fixen) Schwellenwerte EINMAL auf das Test-Set anwenden
    test_probs, test_labels = get_probs_and_labels(model, test_loader, device)
    threshold_results = evaluate_with_thresholds(test_probs, test_labels, thresholds)
    print_threshold_report(threshold_results)