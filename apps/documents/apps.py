
# =============================================================================
# apps/documents/apps.py - CONFIGURACIÓN DE LA APLICACIÓN
# =============================================================================

from django.apps import AppConfig

class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.documents'
    verbose_name = 'Gestión de Documentos'
    # Sin señales: solo activaban al empleado en prueba al aprobar sus
    # documentos (saltándose los 60 días + evaluación) y escribían logs.