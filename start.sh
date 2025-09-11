#!/bin/sh
set -e

# Instala libmagic para python-magic
apt-get update && apt-get install -y libmagic1

# Ejecuta migraciones
python manage.py migrate

# Inicia Gunicorn
exec gunicorn config.wsgi
