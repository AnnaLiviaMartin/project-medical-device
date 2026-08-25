"""
Inferenz-Logik fuer das MedIC-Chest-X-ray-Modell.

Fast 1:1 uebernommen aus dem urspruenglichen Django-Backend
(ml/services.py::run_model_on_image). Zwei Unterschiede:

  1. Keine Abhaengigkeit mehr von Django (kein `from django.conf import
     settings`), Konfiguration stattdessen ueber Umgebungsvariablen.
  2. Grad-CAM-Overlays werden nicht mehr als Datei ins MEDIA_ROOT
     geschrieben, sondern als Base64-PNG im Response-JSON zurueckgegeben.
     Das Java-Backend (RestMlAnalysisService) uebernimmt das Abspeichern
     ueber denselben FileStorageService, der auch fuer die simulierte
     Analyse verwendet wird - der Microservice bleibt damit zustandslos.
"""

import base64
import os
import sys
from io import BytesIO
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

# Erwartete Verzeichnisstruktur (siehe README.md in diesem Ordner):
#   ml-service/
#     app/inference.py          <- diese Datei
#     machine_learning/
#       nih_train.py            <- unveraendert aus dem alten Projekt
#       constants.py            <- unveraendert aus dem alten Projekt
#       checkpoints/best_model.pt
ML_DIR = Path(__file__).resolve().parent.parent / "machine_learning"
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from nih_train import get_model  # type: ignore  # noqa: E402
from constants import IMAGENET_MEAN, IMAGENET_STD, PATHOLOGY_LIST, PIXEL  # type: ignore  # noqa: E402

NUM_CLASSES = len(PATHOLOGY_LIST)

# Bewusst derselbe Default wie auf der Java-Seite (SimulatedMlAnalysisService),
# damit beide Implementierungen hinter derselben Schnittstelle konsistent
# nur Befunde >= 70% als "positiv" behandeln. Per Env-Var ueberschreibbar.
THRESHOLD = float(os.environ.get("ML_THRESHOLD", "0.5"))

# Optional per Env-Var ueberschreibbar, z. B. wenn der Checkpoint (der wegen
# seiner Groesse nicht im Docker-Image liegt) per Volume unter einem anderen
# Pfad gemountet wird, statt ihn ins Image zu backen.
MODEL_PATH = Path(
    os.environ.get("ML_MODEL_PATH", str(ML_DIR / "checkpoints" / "best_model.pt"))
)


class ModelLoadError(RuntimeError):
    """Wird geworfen, wenn Checkpoint/Modell nicht geladen werden koennen."""


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

    if not MODEL_PATH.exists():
        raise ModelLoadError(
            f"Checkpoint nicht gefunden unter '{MODEL_PATH}'. "
            f"ML_MODEL_PATH pruefen oder Datei nach machine_learning/checkpoints/ legen."
        )

    device = _get_device()
    model = get_model(num_classes=NUM_CLASSES)

    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state"])
    model = model.to(device)
    model.eval()

    _model = model
    return _model


def _build_transform():
    return transforms.Compose([
        transforms.Resize(PIXEL),
        transforms.CenterCrop(PIXEL),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def _load_image_tensor(pil_image, device):
    transform = _build_transform()
    image_tensor = transform(pil_image)
    image_tensor = image_tensor.unsqueeze(0)
    return image_tensor.to(device)


def _generate_gradcam_map(model, image_tensor, target_index):
    activations = []
    gradients = []

    image_tensor = image_tensor.clone().detach().requires_grad_(True)

    target_layer = model.features

    def forward_hook(module, input, output):
        activations.append(output)
        output.register_hook(lambda grad: gradients.append(grad))

    handle_f = target_layer.register_forward_hook(forward_hook)

    model.zero_grad()
    output = model(image_tensor)
    score = output[0, target_index]
    score.backward(retain_graph=True)

    handle_f.remove()

    if not activations or not gradients:
        raise RuntimeError(
            "Grad-CAM: Keine Aktivierungen/Gradienten am Ziellayer erfasst. "
            "Pruefe, ob 'model.features' im Forward-Pfad liegt und nicht "
            "vollstaendig eingefroren ist."
        )

    acts = activations[0].detach()[0]
    grads = gradients[0].detach()[0]
    weights = grads.mean(dim=(1, 2))

    cam = torch.zeros(acts.shape[1:], dtype=torch.float32)
    for i, w in enumerate(weights):
        cam += w * acts[i]

    cam = torch.relu(cam)
    cam -= cam.min()
    if cam.max() > 0:
        cam /= cam.max()

    return cam.cpu().numpy()


def _overlay_heatmap(base_image, cam, alpha=0.45):
    cam_resized = Image.fromarray((cam * 255).astype(np.uint8)).resize(base_image.size)
    cam_arr = np.array(cam_resized).astype(np.float32) / 255.0

    heatmap = np.zeros((*cam_arr.shape, 3), dtype=np.uint8)
    heatmap[..., 0] = (cam_arr * 255).astype(np.uint8)
    heatmap[..., 2] = ((1 - cam_arr) * 255).astype(np.uint8)

    heatmap_img = Image.fromarray(heatmap).convert("RGB")
    base = base_image.convert("RGB")
    return Image.blend(base, heatmap_img, alpha)


def _image_to_base64_png(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def run_model_on_image(image_path) -> dict:
    """Fuehrt Inferenz + Grad-CAM aus und liefert ein JSON-serialisierbares dict.

    Form entspricht dem, was RestMlAnalysisService.java (Java-Seite) erwartet:
      {
        "label": str,
        "confidence": float,
        "threshold": float,
        "scores": {pathology: float, ...},
        "gradcam_images": {pathology: "<base64 png>", ...}   # nur >= threshold
      }
    """
    device = _get_device()
    model = _load_model()

    pil_image = Image.open(image_path).convert("RGB")
    image_tensor = _load_image_tensor(pil_image, device)

    with torch.no_grad():
        logits = model(image_tensor)
    probabilities = torch.sigmoid(logits)[0]

    scores = {}
    for pathology, probability in zip(PATHOLOGY_LIST, probabilities):
        scores[pathology] = round(probability.item(), 4)

    best_pathology = max(scores, key=scores.get)
    best_confidence = scores[best_pathology]

    positive_findings = {
        pathology: score for pathology, score in scores.items() if score >= THRESHOLD
    }

    resized_base = pil_image.resize((PIXEL, PIXEL))
    gradcam_images = {}

    for pathology in positive_findings:
        target_index = PATHOLOGY_LIST.index(pathology)
        cam = _generate_gradcam_map(model, image_tensor, target_index)
        overlay = _overlay_heatmap(resized_base, cam)
        gradcam_images[pathology] = _image_to_base64_png(overlay)

    return {
        "label": best_pathology if best_confidence >= THRESHOLD else "No Finding",
        "confidence": best_confidence,
        "threshold": THRESHOLD,
        "scores": scores,
        "gradcam_images": gradcam_images,
    }
