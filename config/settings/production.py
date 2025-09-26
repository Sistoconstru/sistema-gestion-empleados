from .base import *

import dj_database_url

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
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

AWS_QUERYSTRING_AUTH = True

DEFAULT_FILE_STORAGE = 'apps.storages_backends.MediaStorage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'