#!/bin/sh
set -e


# Ejecuta migraciones
python manage.py migrate

# Crea superusuario automáticamente si no existe
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
	python manage.py createsuperuser \
		--noinput \
		--username "$DJANGO_SUPERUSER_USERNAME" \
		--email "$DJANGO_SUPERUSER_EMAIL" || true
fi

# Inicia Gunicorn en modo producción
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
