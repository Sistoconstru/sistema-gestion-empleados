from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        import logging
        from django.conf import settings
        from django.core.files.storage import default_storage
        logging.getLogger('django').info(f"[CoreConfig.ready] DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', None)}")
        logging.getLogger('django').info(f"[CoreConfig.ready] Backend de almacenamiento activo: {default_storage.__class__}")
