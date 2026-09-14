# Project: Inference Service

A small FastAPI wrapper around the original PyTorch/DenseNet model, including Grad-CAM (`ml/services.py` from the old Django backend). It is called via REST by the Spring Boot backend using `RestMlAnalysisService`; see the `MlAnalysisService` interface there.

## Setup

### 1. Place the model assets in the correct location

```
ml-service/
  machine_learning/
    checkpoints/
      best_model.pt            <- trained checkpoint
```

### 2. Install dependencies

```bash
cd ml-service
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Starting

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Quick check: `curl http://localhost:8000/health` should return `{‘status’:‘ok’}`. `GET /docs` displays the interactive Swagger UI.

### 4. Switch the Java backend to this

In `application.properties` (or via an environment variable):

```properties
ml.analysis.provider=rest
ml.service.url=http://localhost:8000
```

Without this change, `SimulatedMlAnalysisService` remains active (by default) – this means the Java backend can still be started without the ML service running.

## Configuration (environment variables)

| Variable         | Default                                          | Bedeutung                                   |
|-------------------|---------------------------------------------------|----------------------------------------------|
| `ML_MODEL_PATH`   | `machine_learning/checkpoints/best_model.pt`      | Path to checkpoint                         |
| `ML_THRESHOLD`    | `0.7`                                              | At what probability is a test result considered ‘positive’? |

## API

### `POST /analyze`

Multipart upload, field name `file` (PNG/JPEG).

Response:

```json
{
  "label": "Effusion",
  "confidence": 0.83,
  "threshold": 0.7,
  "scores": { "Atelectasis": 0.12, "Effusion": 0.83, "...": "..." },
  "gradcam_images": { "Effusion": "<base64-encoded PNG>" }
}
```

`gradcam_images` contains only pathologies with a score >= `threshold` – each with its own Grad-CAM overlay (similar to the old Django logic, except that the image is returned directly in the response rather than being stored in `MEDIA_ROOT`; the Java backend handles the storage).

### `GET /health`

For monitoring/Docker health checks.