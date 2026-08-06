from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'

    def ready(self):
        # Registrar signals de push (novedad aprobada, ausencia registrada)
        from . import push_signals  # noqa: F401
