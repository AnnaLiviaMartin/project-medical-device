#!/bin/bash
# Wird von Azure App Service beim Start ausgeführt.
# In Azure Portal: App Service -> Configuration -> General settings -> Startup Command
# dort eintragen: bash startup.sh
# (Datei muss im Projekt-Root liegen, neben manage.py)

python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn config.wsgi:application --bind=0.0.0.0:8000 --timeout 600