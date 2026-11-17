from django.apps import AppConfig


class TransporteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.transporte'
    verbose_name = 'Transporte'

    def ready(self):
        from . import signals  # noqa: F401
