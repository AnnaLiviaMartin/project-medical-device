#!/bin/sh
set -e

if [ "$DJANGO_SECRET_KEY" = "" ] && [ "$DJANGO_DEBUG" != "True" ]; then
    echo "WARNUNG: DJANGO_SECRET_KEY ist nicht gesetzt - es wird der unsichere Dev-Key verwendet." >&2
fi

if [ ! -f "/app/machine_learning/checkpoints/best_model.pt" ] && [ "$ML_MODEL_PATH" = "" ]; then
    echo "WARNUNG: Kein ML-Modell-Checkpoint unter machine_learning/checkpoints/best_model.pt gefunden." >&2
    echo "         Predictions werden fehlschlagen, bis er vorhanden ist (Image backen oder ML_MODEL_PATH setzen)." >&2
fi

echo "Fuehre Datenbank-Migrationen aus..."
python manage.py migrate --noinput

echo "Sammle Static Files..."
python manage.py collectstatic --noinput

echo "Starte gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-1}" \
    --threads "${GUNICORN_THREADS:-2}" \
    --timeout "${GUNICORN_TIMEOUT:-120}"
