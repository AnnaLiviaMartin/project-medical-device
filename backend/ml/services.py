def run_model_on_image(image_path: str) -> dict:
    # TODO: Hier später echtes Modell laden und inferieren
    return {
        "label": "normal",
        "confidence": 0.93,
        "details": {
            "model_version": "v1",
        },
    }
