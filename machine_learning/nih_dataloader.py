# convolutional neural network
# nih chest x-ray

import os
import pandas as pd
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from constants import PATHOLOGY_LIST, NUM_CLASSES
from pathlib import Path

"""
NIH Chest X-ray Dataset — Data Pipeline
========================================
Vorausgesetzte Verzeichnisstruktur:
    data/
    ├── images/                  # alle .png Röntgenbilder
    ├── Data_Entry_2017.csv
    ├── train_val_list.txt
    └── test_list.txt
"""

# ==============================================================================
# 2. LABELS AUFBEREITEN (One/Multi-Hot-Encoding)
# ==============================================================================

def load_and_encode_labels(csv_path: str) -> pd.DataFrame:
    """
    Liest Data_Entry_2017.csv und wandelt die Pipe-getrennten Labels
    in einen One-Hot-Encoded DataFrame um.

    Beispiel:
        "Atelectasis|Infiltration" → [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    Rückgabe:
        DataFrame mit Spalten: ['Image Index', 'Patient ID', *PATHOLOGY_LIST]
    """
    df = pd.read_csv(csv_path)

    # One-Hot-Encoding: für jede Pathologie eine eigene Binär-Spalte anlegen
    for pathology in PATHOLOGY_LIST:
        # Prüft ob die Pathologie im Label-String vorkommt
        df[pathology] = df["Finding Labels"].apply(
            lambda labels: 1 if pathology in labels.split("|") else 0
        )

    # Nur relevante Spalten behalten
    cols = ["Image Index", "Patient ID"] + PATHOLOGY_LIST
    df = df[cols].copy()

    # Sanity Check: Zeige Klassenverteilung
    print("=== Klassenverteilung im Gesamtdatensatz ===")
    label_counts = df[PATHOLOGY_LIST].sum().sort_values(ascending=False)
    total = len(df)
    for name, count in label_counts.items():
        print(f"  {name:<22}: {count:>6} ({count/total*100:.1f}%)")
    print(f"\n  Gesamt Bilder: {total}")
    print(f"  'No Finding':  {(df[PATHOLOGY_LIST].sum(axis=1) == 0).sum()}")

    return df


# ==============================================================================
# 3. PATIENT-LEVEL SPLIT
# ==============================================================================

def split_dataframe(
    df: pd.DataFrame,
    train_list_path: str,
    test_list_path: str,
    val_fraction: float = 0.1,
    random_seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Teilt den DataFrame in Train / Val / Test auf Patienten-Ebene.

    WICHTIG: Nutzt die offiziellen NIH-Listen, sodass Bilder desselben
    Patienten niemals in verschiedenen Splits landen (Data Leakage vermeiden).

    Args:
        df:               Vollständiger DataFrame aus load_and_encode_labels()
        train_list_path:  Pfad zu train_val_list.txt
        test_list_path:   Pfad zu test_list.txt
        val_fraction:     Anteil der Trainingsbilder, der für Validation genutzt wird
        random_seed:      Für Reproduzierbarkeit

    Returns:
        train_df, val_df, test_df
    """
    with open(train_list_path) as f:
        train_val_files = set(line.strip() for line in f)

    with open(test_list_path) as f:
        test_files = set(line.strip() for line in f)

    # Test-Split
    test_df = df[df["Image Index"].isin(test_files)].reset_index(drop=True)

    # Train+Val-Pool
    train_val_df = df[df["Image Index"].isin(train_val_files)].reset_index(drop=True)

    # Validation-Split auf PATIENTEN-Ebene
    unique_patients = train_val_df["Patient ID"].unique()

    train_patients, val_patients = train_test_split(
        unique_patients,
        test_size=val_fraction,
        random_state=random_seed,
    )

    train_df = train_val_df[
        train_val_df["Patient ID"].isin(train_patients)
    ].reset_index(drop=True)

    val_df = train_val_df[
        train_val_df["Patient ID"].isin(val_patients)
    ].reset_index(drop=True)

    # Zusammenfassung ausgeben
    print("\n=== Split-Größen ===")
    print(f"  Training:   {len(train_df):>6} Bilder  ({train_df['Patient ID'].nunique()} Patienten)")
    print(f"  Validation: {len(val_df):>6} Bilder  ({val_df['Patient ID'].nunique()} Patienten)")
    print(f"  Test:       {len(test_df):>6} Bilder  ({test_df['Patient ID'].nunique()} Patienten)")

    # Sicherheitscheck: keine Patienten-Überschneidungen
    train_patients_set = set(train_df["Patient ID"])
    val_patients_set   = set(val_df["Patient ID"])
    test_patients_set  = set(test_df["Patient ID"])

    assert train_patients_set.isdisjoint(val_patients_set), "FEHLER: Train/Val-Überschneidung!"
    assert train_patients_set.isdisjoint(test_patients_set), "FEHLER: Train/Test-Überschneidung!"
    assert val_patients_set.isdisjoint(test_patients_set),   "FEHLER: Val/Test-Überschneidung!"
    print("\n Kein Data Leakage — alle Splits sind patientenseitig getrennt.")

    return train_df, val_df, test_df


# ==============================================================================
# 4. CLASS WEIGHTS für BCEWithLogitsLoss berechnen
# ==============================================================================

def compute_pos_weights(train_df: pd.DataFrame) -> torch.Tensor:
    """
    Berechnet pos_weight für jede Klasse zur Kompensation des Klassenungleichgewichts.

    pos_weight[i] = Anzahl negativer Beispiele / Anzahl positiver Beispiele

    Dieser Vektor wird direkt an nn.BCEWithLogitsLoss(pos_weight=...) übergeben.
    """
    label_matrix = train_df[PATHOLOGY_LIST].values  # Shape: (N, 14)
    n_total = len(label_matrix)

    print(f"[DEBUG] Dataset size (n_total): {n_total}")
    print(f"[DEBUG] Label matrix shape: {label_matrix.shape} (N, num_classes = {len(PATHOLOGY_LIST)})")

    pos_counts = label_matrix.sum(axis=0)           # Positive pro Klasse
    print("\n[DEBUG] Positive counts per class:")
    for name, c in zip(PATHOLOGY_LIST, pos_counts):
        print(f"  {name:<22}: {int(c)}")

    neg_counts = n_total - pos_counts               # Negative pro Klasse
    print("\n[DEBUG] Negative counts per class:")
    for name, c in zip(PATHOLOGY_LIST, neg_counts):
        print(f"  {name:<22}: {int(c)}")

    # Verhältnis: neg/pos
    pos_weights = neg_counts / np.clip(pos_counts, a_min=1, a_max=None)
    print("\n=== Klassen-Gewichte (pos_weight für BCEWithLogitsLoss) ===")
    for name, pos, neg, w in zip(PATHOLOGY_LIST, pos_counts, neg_counts, pos_weights):
        print(
            f"  {name:<22}: "
            f"neg={int(neg):5d} | pos={int(pos):5d} | weight={w:.3f}"
        )

    return torch.tensor(pos_weights, dtype=torch.float32)


# ==============================================================================
# 5. PYTORCH DATASET
# ==============================================================================

class NIHChestXrayDataset(Dataset):
    """
    PyTorch Dataset für den NIH Chest X-ray Datensatz.

    Args:
        df:          DataFrame mit 'Image Index' und den 14 Pathologie-Spalten
        images_dir:  Pfad zum Ordner mit den .png Bildern
        transform:   torchvision-Transforms (Augmentation + Normalisierung)
    """

    def __init__(self, df: pd.DataFrame, images_dir: str, transform=None):
        self.df = df.reset_index(drop=True)
        self.images_dir = images_dir
        self.transform = transform

        self.image_index = self._build_image_index(images_dir)


    def _build_image_index(self, root_dir):
        index = {}
        for p in Path(root_dir).rglob("*.png"):
            index[p.name] = str(p)
        return index

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]

        filename = row["Image Index"]
        img_path = self.image_index[filename]

        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        labels = torch.tensor(
            row[PATHOLOGY_LIST].values.astype(np.float32),
            dtype=torch.float32,
        )

        return image, labels


# ==============================================================================
# 6. TRANSFORMS & AUGMENTATION
# ==============================================================================

def get_transforms(mode: str = "train") -> transforms.Compose:
    """
    Gibt die richtigen Transforms für Training oder Validation/Test zurück.
    """
    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std  = [0.229, 0.224, 0.225]

    if mode == "train":
        return transforms.Compose([
            transforms.Resize(224),
            transforms.RandomCrop(224),
            transforms.RandomHorizontalFlip(p=0.5), # so kann Herz auf der falschen Seite erscheinen, was die Klassifikation erschwert?
            transforms.RandomRotation(degrees=5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
        ])
    else:  # val / test
        return transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
        ])


# ==============================================================================
# 7. DATALOADER FACTORY
# ==============================================================================

def create_dataloaders(
    data_dir: str,
    batch_size: int = 32, # TODO 64?
    num_workers: int = 4,
    val_fraction: float = 0.1,
    random_seed: int = 42,
) -> tuple[DataLoader, DataLoader, DataLoader, torch.Tensor]:
    """
    Vollständige Pipeline: CSV lesen → splitten → Datasets → DataLoaders.

    Args:
        data_dir:     Wurzelverzeichnis mit CSV, txt-Listen und images/-Ordner
        batch_size:   Batch-Größe für alle Loader
        num_workers:  Parallel-Prozesse für Datenladen
        val_fraction: Anteil des Train-Pools für Validation
        random_seed:  Für Reproduzierbarkeit

    Returns:
        train_loader, val_loader, test_loader, pos_weights
    """
    csv_path        = os.path.join(data_dir, "Data_Entry_2017.csv")
    train_list_path = os.path.join(data_dir, "train_val_list.txt")
    test_list_path  = os.path.join(data_dir, "test_list.txt")
    images_dir      = os.path.join(data_dir, "images")

    # Schritt 1: Labels laden und encodieren
    df = load_and_encode_labels(csv_path)

    # Schritt 2: Patient-Level Split
    train_df, val_df, test_df = split_dataframe(
        df, train_list_path, test_list_path, val_fraction, random_seed
    )

    # Schritt 3: Class Weights berechnen
    pos_weights = compute_pos_weights(train_df)

    # Schritt 4: Datasets erstellen
    train_dataset = NIHChestXrayDataset(train_df, images_dir, transform=get_transforms("train"))
    val_dataset   = NIHChestXrayDataset(val_df,   images_dir, transform=get_transforms("val"))
    test_dataset  = NIHChestXrayDataset(test_df,  images_dir, transform=get_transforms("test"))

    # Schritt 5: DataLoader erstellen
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,         # Beschleunigt GPU-Transfer
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    print(f"\n=== DataLoader bereit ===")
    print(f"  Train-Batches: {len(train_loader)}")
    print(f"  Val-Batches:   {len(val_loader)}")
    print(f"  Test-Batches:  {len(test_loader)}")

    return train_loader, val_loader, test_loader, pos_weights
