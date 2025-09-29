from .base import *

# Configuración de AWS S3 y backend de almacenamiento
DEFAULT_FILE_STORAGE = 'custom_storage.MediaStorage'

# Log para verificar el settings activo y el backend de almacenamiento
import os
import logging
from django.conf import settings
from django.core.files.storage import default_storage

logging.getLogger('django').info(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
logging.getLogger('django').info(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', None)}")
logging.getLogger('django').info(f"Backend de almacenamiento activo: {default_storage.__class__}")

import dj_database_url

# Prueba de logging manual
logging.getLogger('storages').debug('Prueba de logging storages desde Railway')
logging.getLogger('django').info('Prueba de logging django desde Railway')

DEBUG = False

ALLOWED_HOSTS = [
    'empleados.sistemaconstruinmuniza.com',
    'localhost',
    '127.0.0.1',
    os.environ.get('RAILWAY_DOMAIN', ''),  # Agrega el dominio Railway si aplica
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
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

DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}


INSTALLED_APPS += ['storages']

# Configuración de AWS S3
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'sa-east-1')  # Ejemplo: 'sa-east-1' para São Paulo
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.sa-east-1.amazonaws.com'

AWS_QUERYSTRING_AUTH = True

DEFAULT_FILE_STORAGE = 'storages_backends.MediaStorage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'