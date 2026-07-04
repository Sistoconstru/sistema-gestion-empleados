from .base import *

# Configuración de storage para producción
DEFAULT_FILE_STORAGE = 'custom_storage.media.MediaStorage'

# Log para verificar el settings activo
import os
import logging
from django.conf import settings

logging.getLogger('django').info(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
logging.getLogger('django').info(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', None)}")

import dj_database_url

# Prueba de logging manual
logging.getLogger('storages').debug('Prueba de logging storages desde Railway')
logging.getLogger('django').info('Prueba de logging django desde Railway')

DEBUG = False

ALLOWED_HOSTS = [h for h in [
    'empleados.sistemaconstruinmuniza.com',
    'localhost',
    '127.0.0.1',
    'sighu-web.railway.internal',  # Red privada Railway: Odoo llama por este host
    os.environ.get('RAILWAY_DOMAIN', ''),  # URL temporal de Railway o dominio custom
] if h]

# CSRF: hosts permitidos para POST/PUT/DELETE con cookies cross-origin (Django >= 4.0)
CSRF_TRUSTED_ORIGINS = [
    'https://empleados.sistemaconstruinmuniza.com',
]
_railway_domain = os.environ.get('RAILWAY_DOMAIN', '')
if _railway_domain and not _railway_domain.startswith('http'):
    CSRF_TRUSTED_ORIGINS.append(f'https://{_railway_domain}')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
# Exentos de redirect HTTP→HTTPS: las llamadas Odoo→SIGHU entran por la red
# privada de Railway (*.railway.internal) en HTTP plano. Sin esta exención el
# 301 a HTTPS rompe la integración (Odoo no sigue el redirect / pierde el body).
# Patrón se evalúa contra request.path.lstrip('/').
SECURE_REDIRECT_EXEMPT = [
    r'^api/v1/odoo/',
]
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Cache local (puedes cambiar a Redis si lo necesitas)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# Logging para producción (a consola, recomendado en Railway)
import logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'storages': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'boto3': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'botocore': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
LOGOUT_REDIRECT_URL = '/auth/login/'

# Database configuration for Railway
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    import logging
    logging.warning('WARNING: DATABASE_URL environment variable is not set, databases will not be configured')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.dummy',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }


INSTALLED_APPS += ['storages']

# Configuración de AWS S3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'sa-east-1')  # Ejemplo: 'sa-east-1' para São Paulo
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.sa-east-1.amazonaws.com'

AWS_QUERYSTRING_AUTH = True

## Línea eliminada para evitar sobrescritura del backend
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'