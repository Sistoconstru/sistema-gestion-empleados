
# =============================================================================
# apps/documents/apps.py - CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================

from django.apps import AppConfig

class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.documents'
    verbose_name = 'Gestión de Documentos'
    
    def ready(self):
        """Configurar señales cuando la app esté lista"""
        import apps.documents.signals