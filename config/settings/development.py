
# =============================================================================
# config/settings/development.py - CONFIGURACIÓN ESPECÍFICA PARA DESARROLLO
# =============================================================================

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# =============================================================================
# CONFIGURACIÓN DE STORAGE PARA DESARROLLO (LOCAL)
# =============================================================================
# En desarrollo usamos almacenamiento local en lugar de S3
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Patch para modelos que tienen storage explícito de S3 en desarrollo
import os
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings.development':
    # Sobrescribir storage de S3 para desarrollo
    try:
        from django.core.files.storage import FileSystemStorage
        # Crear storage local para desarrollo
        local_storage = FileSystemStorage()
        
        # Monkey patch para el MediaStorage usado en modelos
        import custom_storage.media
        custom_storage.media.MediaStorage = lambda: local_storage
    except ImportError:
        pass

# Sobrescribir configuración de base de datos para desarrollo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sighu_produccion',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'client_encoding': 'UTF8',
            # Configuración más simple sin transaction isolation
        }
    }
}

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache para desarrollo
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# CORS settings para desarrollo
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
LOGOUT_REDIRECT_URL = '/auth/login/'