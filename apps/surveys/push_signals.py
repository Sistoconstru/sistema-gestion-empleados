"""Signals que disparan notificaciones cuando se publica una encuesta.

Estrategia:
- Al pasar `Encuesta.activa` a True (o crearla ya activa), notificar a
  los destinatarios (según asignación por cargo/área).
- La lista de destinatarios se calcula con el helper _destinatarios_encuesta.
- Idempotencia: usamos un flag en cache local del modelo (`_activa_anterior`)
  para saber si el `save` cambió el estado; y un tag en la Notificacion para
  no duplicar aunque se reguarde el objeto.
"""
import logging

from django.db.models.signals import post_init, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_init, sender='surveys.Encuesta')
def _recordar_estado_activa(sender, instance, **kwargs):
    """Guarda el valor de `activa` cargado desde BD para detectar transiciones."""
    instance._activa_anterior = instance.activa if instance.pk else None


@receiver(post_save, sender='surveys.Encuesta')
def _notificar_publicacion(sender, instance, created, **kwargs):
    """Notifica al destinatario cuando la encuesta entra en estado activa.

    Casos:
    - created=True + activa=True → publicación inicial.
    - created=False + antes False + ahora True → reactivación (también notifica).
    - Cualquier otro → no notifica.
    """
    antes = getattr(instance, '_activa_anterior', None)
    entro_en_activa = instance.activa and (created or antes is not True)
    if not entro_en_activa:
        return

    try:
        from .views import _destinatarios_encuesta
        from apps.notifications.models import Notificacion, TipoNotificacion
        from apps.notifications.push_utils import send_push
    except ImportError:
        return

    destinatarios = list(_destinatarios_encuesta(instance))
    if not destinatarios:
        logger.info(
            f'Encuesta {instance.codigo} publicada sin destinatarios asignados; no se notifica.'
        )
        return

    tipo_notif, _ = TipoNotificacion.objects.get_or_create(
        codigo='encuesta_publicada',
        defaults={
            'nombre': 'Encuesta publicada',
            'descripcion': 'Notificación cuando se publica una encuesta al empleado.',
            'plantilla_titulo': 'Nueva encuesta disponible',
            'plantilla_mensaje': 'Tienes una encuesta pendiente.',
            'enviar_email': False,
            'enviar_push': True,
            'activo': True,
        },
    )

    titulo = 'Nueva encuesta disponible'
    cuerpo = (
        f'{instance.nombre}. Cierra el {instance.fecha_fin:%d/%m/%Y}. '
        f'Toca para responderla.'
    )
    url = f'/encuestas/responder/{instance.pk}/'

    enviadas = 0
    for emp in destinatarios:
        tag = f'encuesta-pub-{instance.pk}-{emp.usuario.pk}'
        if Notificacion.objects.filter(
            usuario=emp.usuario, datos_adicionales__contains={'push_tag': tag},
        ).exists():
            continue
        try:
            envi, _ = send_push(
                emp.usuario, titulo, cuerpo,
                url=url, tag=tag, tag_group='encuesta',
                actions=[{'action': 'responder', 'title': 'Responder'}],
                action_urls={'responder': url},
            )
            Notificacion.objects.create(
                usuario=emp.usuario, tipo_notificacion=tipo_notif,
                titulo=titulo, mensaje=cuerpo,
                datos_adicionales={'push_tag': tag, 'encuesta_id': str(instance.pk)},
            )
            if envi:
                enviadas += 1
        except Exception as e:
            logger.warning(f'Fallo notificando encuesta {instance.codigo} a {emp.usuario.username}: {e}')

    logger.info(
        f'Encuesta {instance.codigo} publicada: {enviadas} push · {len(destinatarios)} destinatarios.'
    )
