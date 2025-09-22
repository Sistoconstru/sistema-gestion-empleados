#!/bin/sh
set -e


# Ejecuta migraciones
python manage.py migrate

# Crea un superusuario si no existe


# Inicia Gunicorn en modo producción
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
