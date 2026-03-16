from django.apps import AppConfig


class EvaluationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.evaluations'

    def ready(self):
        """Importar signals cuando la app esté lista"""
        import apps.evaluations.signals
