from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'  # ← IMPORTANTE: debe incluir 'apps.'
    verbose_name = 'Autenticación y Permisos'