from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        import logging
        from django.conf import settings
        logging.getLogger('django').info(f"[CoreConfig.ready] DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', None)}")

        # Iniciar scheduler de tareas automáticas
        self._iniciar_scheduler_automatico()

    def _iniciar_scheduler_automatico(self):
        """Inicia el scheduler de tareas automáticas de forma segura."""
        try:
            # Solo iniciar en producción (DEBUG=False) o si está explícitamente activado
            from django.conf import settings
            from django.core.management import execute_from_command_line
            import sys

            # No iniciar si se está ejecutando migraciones o test
            if any(cmd in sys.argv for cmd in ['migrate', 'test', 'makemigrations']):
                return

            # No iniciar si se está ejecutando manage.py (evita inicios duplicados)
            if 'manage.py' in sys.argv:
                return

            # Iniciar el scheduler
            from apps.core.scheduler import start_scheduler
            scheduler = start_scheduler()

            if scheduler and scheduler.running:
                logger.info('✅ Scheduler de evaluaciones iniciado automáticamente')
            else:
                logger.warning('⚠️ No se pudo iniciar el scheduler automáticamente')

        except Exception as e:
            logger.warning(f'⚠️ No se pudo iniciar scheduler automático: {e}')
            # No interrumpir el inicio de Django si falla el scheduler
