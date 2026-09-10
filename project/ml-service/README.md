# Projekt: Inference Service

Kleiner FastAPI-Wrapper um das urspruengliche PyTorch/DenseNet-Modell samt Grad-CAM (`ml/services.py` aus dem alten Django-Backend). Wird vom Spring-Boot-Backend ueber `RestMlAnalysisService` per REST aufgerufen, siehe `MlAnalysisService`-Interface dort.

## Setup

### 1. Modell-Assets an die richtige Stelle legen

```
ml-service/
  machine_learning/
    checkpoints/
      best_model.pt            <- trainierter Checkpoint
```

### 2. Abhaengigkeiten installieren

```bash
cd ml-service
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Starten

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Kurzer Check: `curl http://localhost:8000/health` sollte `{"status":"ok"}` liefern. `GET /docs` zeigt die interaktive Swagger-UI.

### 4. Java-Backend darauf umstellen

In `application.properties` (oder per Env-Var):

```properties
ml.analysis.provider=rest
ml.service.url=http://localhost:8000
```

Ohne diese Umstellung bleibt `SimulatedMlAnalysisService` aktiv (Standard) - so kann das Java-Backend weiter ohne laufenden ML-Service gestartet werden.

## Konfiguration (Umgebungsvariablen)

| Variable         | Default                                          | Bedeutung                                   |
|-------------------|---------------------------------------------------|----------------------------------------------|
| `ML_MODEL_PATH`   | `machine_learning/checkpoints/best_model.pt`      | Pfad zum Checkpoint                         |
| `ML_THRESHOLD`    | `0.7`                                              | Ab welcher Wahrscheinlichkeit ein Befund als "positiv" gilt |

## API

### `POST /analyze`

Multipart-Upload, Feldname `file` (PNG/JPEG).

Response:

```json
{
  "label": "Effusion",
  "confidence": 0.83,
  "threshold": 0.7,
  "scores": { "Atelectasis": 0.12, "Effusion": 0.83, "...": "..." },
  "gradcam_images": { "Effusion": "<base64-kodiertes PNG>" }
}
```

`gradcam_images` enthaelt nur Pathologien, deren Score >= `threshold` ist - fuer jede davon ein eigenes Grad-CAM-Overlay (analog zur alten Django-Logik, nur dass das Bild statt in `MEDIA_ROOT` gespeichert direkt im Response zurueckgegeben wird; das Java-Backend uebernimmt das Abspeichern).

### `GET /health`

Fuer Monitoring/Docker-Healthcheck.