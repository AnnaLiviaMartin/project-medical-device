# Backend
This contains information on the python backend

## Start Backend

Start the backend using:
```bash
python manage.py runserver
```

Open: http://127.0.0.1:8000/ in your browser.

## Delete data

```bash
python manage.py reset_all
```

## Dokumentation of Endpoints
Available Endpoints are: GET/POST/PUT/PATCH/DELETE

## Models
After creating a model run:

```bash
python manage.py makemigrations
python manage.py migrate
```