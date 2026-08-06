# Build von diesem Dockerfile aus dem PROJEKT-ROOT (nicht aus backend/!):
#   docker build -f backend/Dockerfile -t medic-backend .
# Grund: ml/services.py erwartet machine_learning/ als Geschwister-Ordner
# von backend/ (gleiche Struktur wie im Repo), daher muss dieser Ordner
# ebenfalls in den Build-Context / ins Image.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/backend

# Systemabhaengigkeiten fuer Pillow/pydicom. torch-CPU-Wheels bringen ihre
# eigenen Laufzeitbibliotheken bereits mit.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt

# torch/torchvision zuerst gezielt als reine CPU-Wheels installieren.
# Ohne den expliziten --index-url wuerden die Standard-PyPI-Pakete
# installiert, die CUDA-Bibliotheken enthalten (mehrere GB, hier
# unnoetig, da nur CPU-Inferenz bei 4 Requests/Tag benoetigt wird).
RUN pip install --index-url https://download.pytorch.org/whl/cpu \
        torch==2.5.1 torchvision==0.20.1 \
    && pip install -r requirements.txt

COPY backend/ ./
COPY machine_learning/ ../machine_learning/

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
