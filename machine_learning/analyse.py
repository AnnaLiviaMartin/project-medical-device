import json
import os

import torch
from PIL import Image
from torchvision import transforms
from nih_train import get_model
from constants import IMAGENET_MEAN, IMAGENET_STD, PATHOLOGY_LIST, PIXEL, CONFIG

MODEL_PATH = "./checkpoints/best_model.pt"
IMAGE_PATH = "./mein_roentgenbild.png"
THRESHOLDS_PATH = os.path.join(CONFIG["output_dir"], "thresholds.json")

NUM_CLASSES = 14
DEFAULT_THRESHOLD = 0.5  # Fallback, falls thresholds.json (noch) nicht existiert


def load_thresholds(path=THRESHOLDS_PATH):
    """
    Lädt die klassenspezifischen Decision-Thresholds, die ausschließlich auf
    dem Validierungssplit bestimmt wurden (siehe nih_threshold.py). Diese
    werden im Prototyp verwendet, um vorherzusagen, ob ein Befund als
    positiv angezeigt wird — nicht ein pauschaler Wert von 0.5.
    """
    if not os.path.exists(path):
        print(
            f"Warnung: '{path}' nicht gefunden. "
            f"Fällt zurück auf einheitlichen Threshold {DEFAULT_THRESHOLD}. "
            "Führe evaluate_on_test() in nih_train.py einmal aus, um die "
            "Thresholds zu erzeugen."
        )
        return {pathology: DEFAULT_THRESHOLD for pathology in PATHOLOGY_LIST}

    with open(path, encoding="utf-8") as file:
        return json.load(file)

def choose_gpu():
    return torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

def load_image(image_path, device):
    # Bild Transformation
    transform = transforms.Compose([
        transforms.Resize(PIXEL),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image)

    # Batch-Dimension hinzufügen:
    image_tensor = image_tensor.unsqueeze(0)
    image_tensor = image_tensor.to(device)

    return image_tensor

def predict(model, image_tensor):
    with torch.no_grad():
        logits = model(image_tensor)

    # Sigmoid wandelt Logits in Wahrscheinlichkeiten zwischen 0 und 1 um
    probabilities = torch.sigmoid(logits)[0]

    return probabilities

def predict_image(model_path=MODEL_PATH, image_path=IMAGE_PATH):
    device = choose_gpu()

    # Modell laden
    model = get_model(num_classes=NUM_CLASSES)

    checkpoint = torch.load(
    model_path,
    map_location=device,
    weights_only=False,
    )

    model.load_state_dict(checkpoint["model_state"])
    model = model.to(device)
    model.eval()

    print(f"Modell geladen (Epoche {checkpoint['epoch']}, Val-AUC {checkpoint['best_auc']:.4f})")

    # Bild laden und vorbereiten
    image = load_image(image_path, device)

    return predict(model, image)

def print_probabilites(probabilities, thresholds):
    print("\nVorhersagen:")

    for pathology, probability in zip(PATHOLOGY_LIST, probabilities):
        probability_value = probability.item()

        prediction = probability_value >= thresholds[pathology]

        print(
            f"{pathology} "
            f"{probability_value:.4f} "
            f"(Schwelle {thresholds[pathology]:.3f}, "
            f"{'positiv' if prediction else 'negativ'})"
        )

if __name__ == "__main__":
    probabilities = predict_image()
    thresholds = load_thresholds()
    print_probabilites(probabilities, thresholds)