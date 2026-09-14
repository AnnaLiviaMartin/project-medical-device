import logging
import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from .inference import ModelLoadError, run_model_on_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medic-ml-service")

app = FastAPI(
    title="MedIC ML Inference Service",
    description="Wrappt das PyTorch/DenseNet-Modell samt Grad-CAM hinter einem REST-Endpoint, "
                 "der vom Spring-Boot-Backend (RestMlAnalysisService) aufgerufen wird.",
)

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}


@app.get("/health")
def health():
    """Fuer Docker-Healthchecks / manuelles Pruefen, ob der Service laeuft."""
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Nicht unterstuetzter Content-Type: {file.content_type}. "
                   f"Erlaubt: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}.",
        )

    suffix = os.path.splitext(file.filename or "")[1] or ".png"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = run_model_on_image(tmp_path)
        response = JSONResponse(content=result)
        logger.info("ML response media_type: %s", response.media_type)
        logger.info("ML response headers: %s", response.headers)
        return response

    except ModelLoadError as exc:
        logger.error("Modell konnte nicht geladen werden: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - bewusst breit, wird als 500 nach aussen gegeben
        logger.exception("Inferenz fehlgeschlagen")
        raise HTTPException(status_code=500, detail=f"Inferenz fehlgeschlagen: {exc}") from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
