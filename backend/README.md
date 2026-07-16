# Medical Device Backend

This backend provides a Python-based REST API for managing patients, studies, X-ray images, and related machine learning prediction results.

## Technical Support

Start the backend with:

```bash
python manage.py runserver
```

Then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

To delete all development data, run:

```bash
python manage.py reset_all
```

After creating or updating a model, run:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Overview

This backend manages **patients**, **studies**, **X-ray images**, and the corresponding **machine learning results**.

The current workflow is implemented **synchronously**. After an image is uploaded, inference is executed directly within the same request.

## Contents

- [Overview](#overview)
- [Workflow](#workflow)
- [REST Endpoints](#rest-endpoints)
- [Status Values](#status-values)
- [Development Reset](#development-reset)
- [Technical Structure](#technical-structure)

## Workflow

The backend is built around a synchronous request flow:

1. A patient is created.
2. A study is assigned to the patient.
3. An X-ray image is uploaded.
4. Inference is executed immediately.
5. The prediction result is stored and can later be retrieved.

### 1. Create a Patient

First, a patient is created through the REST API.

### 2. Create a Study

A study is then created for that patient.

### 3. Upload an Image

An X-ray image is uploaded and linked to the study.

### 4. Start Inference

Immediately after upload, the machine learning model is executed.

### 5. Store the Result

The prediction result is stored in the database.

### 6. Retrieve the Result

The stored prediction result can be retrieved via a `GET` request.

## REST Endpoints

**Patients**

- `POST /api/patients/`
- `GET /api/patients/`
- `GET /api/patients/{id}/`
- `PATCH /api/patients/{id}/`
- `DELETE /api/patients/{id}/`

**Studies**

- `POST /api/studies/`
- `GET /api/studies/`
- `GET /api/studies/{id}/`

**Images**

- `POST /api/images/`
- `GET /api/images/`
- `GET /api/images/{id}/`

**Prediction Results**

- `GET /api/images/{id}/prediction/`