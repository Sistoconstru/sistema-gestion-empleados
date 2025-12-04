#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE=config.settings.production

# Ejecuta migraciones
python manage.py migrate

# Popula datos iniciales de evaluaciones
python manage.py configurar_evaluaciones_iniciales

# Recopila archivos estáticos (incluye dependencias locales)
python manage.py collectstatic --noinput

# Crea un superusuario si no existe

# Inicia Gunicorn en modo producción
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
