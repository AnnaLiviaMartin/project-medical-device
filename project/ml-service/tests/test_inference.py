"""
Tests for app/inference.py - the actual model-loading, transform and Grad-CAM logic.

Unlike test_main.py these tests need the *real* ML stack (torch, torchvision) because
inference.py imports machine_learning/nih_train.py at module level, which in turn needs
torch/torchvision/scikit-learn. `pytest.importorskip` makes the whole module skip
cleanly (instead of erroring) in an environment where those heavy, optional
dependencies aren't installed

To keep these tests fast and independent of the trained checkpoint , `_load_model` is monkeypatched
with a tiny freshly-initialised model that has the same shape contract
(`model.features` -> conv feature map, `model(x)` -> (1, NUM_CLASSES) logits) instead
of the real DenseNet-121.
"""
import base64
from io import BytesIO
import pytest
from PIL import Image
from pathlib import Path
from app import inference
import numpy as np

torch = pytest.importorskip("torch")
nn = torch.nn

class TinyFakeModel(nn.Module):
    """Minimal stand-in for the real DenseNet-121: same `.features` + callable contract,
    small enough to run instantly on CPU with random weights."""

    def __init__(self, num_classes: int):
        super().__init__()
        self.features = nn.Sequential(nn.Conv2d(3, 4, kernel_size=3, padding=1), nn.ReLU())
        self.classifier = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(4, num_classes))

    def forward(self, x):
        return self.classifier(self.features(x))


@pytest.fixture(autouse=True)
def reset_model_cache(monkeypatch):
    """inference.py caches `_model`/`_device` at module level - make sure each test
    starts from a clean slate instead of reusing another test's monkeypatched model."""
    monkeypatch.setattr(inference, "_model", None)
    monkeypatch.setattr(inference, "_device", None)
    yield
    monkeypatch.setattr(inference, "_model", None)
    monkeypatch.setattr(inference, "_device", None)


@pytest.fixture
def sample_image():
    return Image.new("RGB", (400, 300), color=(120, 130, 140))


class TestBuildTransform:
    def test_resizes_and_normalizes_to_expected_tensor_shape(self, sample_image):
        transform = inference._build_transform()

        tensor = transform(sample_image)

        assert tensor.shape == (3, inference.PIXEL, inference.PIXEL)
        assert tensor.dtype == torch.float32


class TestLoadImageTensor:
    def test_adds_batch_dimension_and_moves_to_device(self, sample_image):
        device = torch.device("cpu")

        tensor = inference._load_image_tensor(sample_image, device)

        assert tensor.shape == (1, 3, inference.PIXEL, inference.PIXEL)
        assert tensor.device == device


class TestImageToBase64Png:
    def test_roundtrips_to_an_identical_image(self, sample_image):
        encoded = inference._image_to_base64_png(sample_image)

        decoded_bytes = base64.b64decode(encoded)
        decoded_image = Image.open(BytesIO(decoded_bytes))

        assert decoded_image.size == sample_image.size
        assert decoded_image.format == "PNG"


class TestOverlayHeatmap:
    def test_returns_rgb_image_matching_base_image_size(self, sample_image):
        cam = torch.rand(10, 10).numpy()

        overlay = inference._overlay_heatmap(sample_image, cam)

        assert overlay.mode == "RGB"
        assert overlay.size == sample_image.size

    def test_alpha_zero_keeps_the_original_image_untouched(self, sample_image):
        cam = torch.rand(10, 10).numpy()

        overlay = inference._overlay_heatmap(sample_image, cam, alpha=0.0)

        assert np.array_equal(
            np.asarray(overlay),
            np.asarray(sample_image.convert("RGB")),
        )


class TestLoadModel:
    def test_raises_model_load_error_when_checkpoint_file_is_missing(self, monkeypatch, tmp_path):
        monkeypatch.setattr(inference, "MODEL_PATH", tmp_path / "does-not-exist.pt")

        with pytest.raises(inference.ModelLoadError, match="does-not-exist.pt"):
            inference._load_model()

    def test_caches_the_loaded_model_across_calls(self, monkeypatch):
        tiny = TinyFakeModel(num_classes=inference.NUM_CLASSES)
        load_calls = []

        def fake_get_model(num_classes):
            load_calls.append(num_classes)
            return tiny

        monkeypatch.setattr(inference, "MODEL_PATH", Path(__file__))
        monkeypatch.setattr(inference, "get_model", fake_get_model)
        monkeypatch.setattr(torch, "load", lambda *a, **k: {"model_state": tiny.state_dict()})

        first = inference._load_model()
        second = inference._load_model()

        assert first is second
        assert len(load_calls) == 1  # get_model() only called once, second call hits the cache


class TestRunModelOnImage:
    def test_returns_expected_shape_and_only_gradcams_positive_findings(self, monkeypatch, tmp_path, sample_image):
        tiny = TinyFakeModel(num_classes=inference.NUM_CLASSES)
        monkeypatch.setattr(inference, "_model", tiny)
        monkeypatch.setattr(inference, "_device", torch.device("cpu"))
        monkeypatch.setattr(inference, "THRESHOLD", 2.0)  # sigmoid output is always < 2.0 -> no positives

        image_path = tmp_path / "xray.png"
        sample_image.save(image_path)

        result = inference.run_model_on_image(str(image_path))

        assert set(result.keys()) == {"label", "confidence", "threshold", "scores", "gradcam_images"}
        assert set(result["scores"].keys()) == set(inference.PATHOLOGY_LIST)
        assert result["label"] == "No Finding"  # nothing reached the (deliberately unreachable) threshold
        assert result["gradcam_images"] == {}

    def test_generates_a_gradcam_image_for_each_positive_finding(self, monkeypatch, tmp_path, sample_image):
        tiny = TinyFakeModel(num_classes=inference.NUM_CLASSES)
        monkeypatch.setattr(inference, "_model", tiny)
        monkeypatch.setattr(inference, "_device", torch.device("cpu"))
        monkeypatch.setattr(inference, "THRESHOLD", -10.0)  # sigmoid output is always >= this -> all positive

        image_path = tmp_path / "xray.png"
        sample_image.save(image_path)

        result = inference.run_model_on_image(str(image_path))

        assert set(result["gradcam_images"].keys()) == set(inference.PATHOLOGY_LIST)
        for encoded in result["gradcam_images"].values():
            decoded = Image.open(BytesIO(base64.b64decode(encoded)))
            assert decoded.size == (inference.PIXEL, inference.PIXEL)
