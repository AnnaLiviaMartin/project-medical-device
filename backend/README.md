# Backend
This contains information on the python backend

## Start Backend

Start the backend using:
```bash
python manage.py runserver
```

Open: http://127.0.0.1:8000/ in your browser.
## Dokumentation of Endpoints
Available Endpoints are:

GET /api/patients
POST /api/patients
GET /api/patients/{id}
PUT/PATCH /api/patients/{id}
DELETE /api/patients/{id}

## Models
After creating a model run:

```bash
python manage.py makemigrations
python manage.py migrate
```