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

        # El scheduler NO se arranca aquí a propósito. Lo lanza start.sh como
        # proceso aparte (`manage.py start_scheduler --daemon`), que es su
        # único dueño.
        #
        # Antes se arrancaba también en este `ready()`, que corre en cada
        # proceso de Gunicorn. Había un intento de evitar el doble arranque,
        # `if 'manage.py' in sys.argv: return`, pero protegía justo el caso
        # contrario: bajo Gunicorn el argv es ['gunicorn', 'config.wsgi...'],
        # no contiene 'manage.py', así que el guardia no hacía nada y quedaban
        # dos planificadores vivos. Cada tarea corría dos veces y todo el mundo
        # recibía las notificaciones duplicadas: 6.384 copias de más sobre
        # 14.583 notificaciones, siempre exactamente 2 por aviso.
        #
        # Si alguna vez hiciera falta un scheduler dentro del proceso web,
        # primero hay que quitarlo de start.sh: dos dueños vuelven a duplicar,
        # y con más de un worker de Gunicorn se multiplicaría por worker.
