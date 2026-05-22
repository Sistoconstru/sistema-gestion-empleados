from django.apps import AppConfig


class OdooIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integraciones.odoo'
    label = 'integraciones_odoo'
    verbose_name = 'Integración Odoo'

    def ready(self):
        from . import signals  # noqa: F401
