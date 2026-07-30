import sys
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

ML_DIR = Path(__file__).resolve().parent.parent.parent / "machine_learning"
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from nih_train import get_model
from constants import IMAGENET_MEAN, IMAGENET_STD, PATHOLOGY_LIST, PIXEL

MODEL_PATH = ML_DIR / "checkpoints" / "best_model.pt"
NUM_CLASSES = 14
THRESHOLD = 0.5

_device = None
_model = None


def _get_device():
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device


def _load_model():
    global _model
    if _model is not None:
        return _model

    device = _get_device()
    model = get_model(num_classes=NUM_CLASSES)

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=device,
        weights_only=False,
    )

    model.load_state_dict(checkpoint["model_state"])
    model = model.to(device)
    model.eval()

    _model = model
    return _model


def _load_image_tensor(image_path, device):
    transform = transforms.Compose([
        transforms.Resize(PIXEL),
        transforms.CenterCrop(PIXEL),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image)
    image_tensor = image_tensor.unsqueeze(0)
    image_tensor = image_tensor.to(device)

    return image_tensor


def run_model_on_image(image_path):
    device = _get_device()
    model = _load_model()

    image_tensor = _load_image_tensor(image_path, device)

    with torch.no_grad():
        logits = model(image_tensor)

    probabilities = torch.sigmoid(logits)[0]

    scores = {}
    for pathology, probability in zip(PATHOLOGY_LIST, probabilities):
        scores[pathology] = round(probability.item(), 4)

    best_pathology = max(scores, key=scores.get)
    best_confidence = scores[best_pathology]

    positive_findings = {
        pathology: score
        for pathology, score in scores.items()
        if score >= THRESHOLD
    }

    return {
        "label": best_pathology if best_confidence >= THRESHOLD else "No Finding",
        "confidence": best_confidence,
        "raw_result": {
            "scores": scores,
            "positive_findings": positive_findings,
            "threshold": THRESHOLD,
        },
    }