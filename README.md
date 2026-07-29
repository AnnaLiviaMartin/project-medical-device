# Cloud-based analysis of X-ray images, with a focus on usability and regulatory requirements

A prototype medical imaging project combining a Django backend, a Next.js frontend, and PyTorch-based machine learning for chest X-ray analysis.

## Repository structure

- `backend/` — Django application and API support
- `frontend/` — Next.js React UI for image display and analysis reporting
- `machine_learning/` — PyTorch training, data loading, and evaluation scripts for the NIH Chest X-ray dataset

## What this project does

- Provides a user-facing review interface for chest X-ray analysis results
- Implements a backend foundation with Django
- Includes an X-ray data pipeline and DenseNet-based PyTorch model for multi-label pathology prediction
- Supports training, checkpointing, and test evaluation for NIH Chest X-ray

## Key components

### Frontend
- ToDo

### Backend
- ToDo

### Machine learning
- `machine_learning/nih_dataloader.py` — NIH dataset loader, label encoding, and patient-level split
- `machine_learning/nih_train.py` — DenseNet-121 training loop, validation, checkpointing, and test evaluation
- `machine_learning/x-ray-analysis.py` — evaluation entrypoint for the trained model
- `machine_learning/nih-visualize.py` — visualization of the model test results
- `machine_learning/constants.py` — pathology list, dataset config, and training hyperparameters

## Setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` after starting the development server.

### Backend

ToDo

### Machine learning

Install the required Python packages for training and evaluation.

```bash
cd machine_learning
python -m venv .venv
.\.venv\Scripts\activate
```

Train or evaluate the model with the available scripts:

```bash
python x-ray-analysis.py
```

#### GPU for training

megagpu-0 RTX A6000

#### Folder for training

/data/stud/2026-MA_project-Martin-Rossel

## Ordner auf HSRM
/data/stud/2026-MA_project-Martin-Rossel

## Get probability of one image

analyse.py -> bild heißt mein_roentgenbild.png

d.h. diese beiden konstanten muss man reingeben in die Mehtode als werte:

MODEL_PATH = "./cnn_state_dict.pt"
IMAGE_PATH = "./mein_roentgenbild.png"

## Usability

Allgemein: https://user-experience-methods.com/05_evaluate/questionnaire.html

Fragebogen: https://www.ueq-online.org/

Zum Vergleich: https://en.wikipedia.org/wiki/System_usability_scale, https://digital.gov/topics/usability/
