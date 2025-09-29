"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""


import os
import logging
logging.basicConfig(level=logging.INFO)
logging.info(f"WSGI DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

# Agregar el directorio raíz al sys.path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Agregar carpeta apps al Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
