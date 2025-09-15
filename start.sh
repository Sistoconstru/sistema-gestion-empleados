#!/bin/sh
set -e


# Ejecuta migraciones
python manage.py migrate

# Carga datos de departamentos y ciudades (solo si existen los archivos)
if [ -f departamentos.json ]; then
	python manage.py loaddata departamentos.json || true
fi
if [ -f ciudades.json ]; then
	python manage.py loaddata ciudades.json || true
fi


# Inicia Gunicorn en modo producción
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
