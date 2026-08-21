"""
Tests for the MedIC ML inference service's HTTP layer (app/main.py).

These tests never touch the real PyTorch model: `run_model_on_image` is mocked
in every case, so the tests are fast and deterministic and focus purely on the
FastAPI endpoints' own responsibilities.
"""
import io
import os
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import ModelLoadError, app

client = TestClient(app)


def _png_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), color="white").save(buffer, format="PNG")
    return buffer.getvalue()


class TestHealth:
    def test_health_returns_ok(self):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAnalyzeHappyPath:
    def test_returns_the_models_result_as_json(self, mocker):
        fake_result = {
            "label": "Cardiomegaly",
            "confidence": 0.87,
            "threshold": 0.5,
            "scores": {"Cardiomegaly": 0.87, "Effusion": 0.12},
            "gradcam_images": {"Cardiomegaly": "base64-placeholder"},
        }
        mocked = mocker.patch("app.main.run_model_on_image", return_value=fake_result)

        response = client.post("/analyze", files={"file": ("xray.png", _png_bytes(), "image/png")})

        assert response.status_code == 200
        assert response.json() == fake_result
        mocked.assert_called_once()

    @pytest.mark.parametrize("content_type", ["image/png", "image/jpeg", "image/jpg"])
    def test_accepts_every_allowed_content_type(self, mocker, content_type):
        mocker.patch("app.main.run_model_on_image", return_value={"label": "No Finding"})

        response = client.post("/analyze", files={"file": ("xray.img", _png_bytes(), content_type)})

        assert response.status_code == 200


class TestAnalyzeValidation:
    def test_rejects_unsupported_content_type_with_400(self, mocker):
        mocked = mocker.patch("app.main.run_model_on_image")

        response = client.post(
            "/analyze",
            files={"file": ("scan.pdf", b"%PDF-1.4 not an image", "application/pdf")},
        )

        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "application/pdf" in detail
        mocked.assert_not_called()

    def test_missing_file_is_rejected_by_fastapi_with_422(self):
        response = client.post("/analyze")

        assert response.status_code == 422


class TestAnalyzeErrorMapping:
    def test_model_load_error_maps_to_503(self, mocker):
        mocker.patch(
            "app.main.run_model_on_image",
            side_effect=ModelLoadError("checkpoint not found under '.../best_model.pt'"),
        )

        response = client.post("/analyze", files={"file": ("xray.png", _png_bytes(), "image/png")})

        assert response.status_code == 503
        assert "checkpoint not found" in response.json()["detail"]

    def test_unexpected_exception_maps_to_500_with_wrapped_message(self, mocker):
        mocker.patch("app.main.run_model_on_image", side_effect=RuntimeError("boom"))

        response = client.post("/analyze", files={"file": ("xray.png", _png_bytes(), "image/png")})

        assert response.status_code == 500
        detail = response.json()["detail"]
        assert "Inferenz fehlgeschlagen" in detail
        assert "boom" in detail


class TestAnalyzeTempFileHandling:
    def test_temp_file_exists_during_inference_and_is_deleted_afterwards(self, mocker):
        seen_paths = []

        def fake_run(image_path):
            seen_paths.append(image_path)
            assert os.path.exists(image_path), "temp file should exist while inference runs"
            return {"label": "No Finding"}

        mocker.patch("app.main.run_model_on_image", side_effect=fake_run)

        response = client.post("/analyze", files={"file": ("xray.png", _png_bytes(), "image/png")})

        assert response.status_code == 200
        assert len(seen_paths) == 1
        assert not os.path.exists(seen_paths[0]), "temp file should be cleaned up after the request"

    def test_temp_file_is_deleted_even_when_inference_raises(self, mocker):
        seen_paths = []

        def fake_run(image_path):
            seen_paths.append(image_path)
            raise RuntimeError("boom")

        mocker.patch("app.main.run_model_on_image", side_effect=fake_run)

        response = client.post("/analyze", files={"file": ("xray.png", _png_bytes(), "image/png")})

        assert response.status_code == 500
        assert not os.path.exists(seen_paths[0]), "temp file must be cleaned up even on failure"

    def test_temp_file_keeps_the_uploaded_files_extension(self, mocker):
        seen_paths = []

        def fake_run(image_path):
            seen_paths.append(image_path)
            return {"label": "No Finding"}

        mocker.patch("app.main.run_model_on_image", side_effect=fake_run)

        client.post("/analyze", files={"file": ("xray.jpeg", _png_bytes(), "image/jpeg")})

        assert seen_paths[0].endswith(".jpeg")

    def test_temp_file_falls_back_to_png_extension_when_filename_has_none(self, mocker):
        seen_paths = []

        def fake_run(image_path):
            seen_paths.append(image_path)
            return {"label": "No Finding"}

        mocker.patch("app.main.run_model_on_image", side_effect=fake_run)

        client.post("/analyze", files={"file": ("noextension", _png_bytes(), "image/png")})

        assert seen_paths[0].endswith(".png")
