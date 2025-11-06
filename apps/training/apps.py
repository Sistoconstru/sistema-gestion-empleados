from django.apps import AppConfig

class TrainingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.training'
    verbose_name = 'Sistema de Capacitaciones'
    
    def ready(self):
        """Importar señales cuando la app esté lista"""
        import apps.training.signals
