"""Signals que disparan notificaciones push ante eventos de negocio.

Tres eventos cubiertos:
- Novedad de nómina aprobada/rechazada → al coordinador que la registró
- Ausencia registrada por el jefe → al empleado
- Recordatorio de sesión de capacitación (se maneja con APScheduler, no signal)

Cada handler carga `send_push` de forma perezosa para que un fallo en un
signal no bloquee el guardado del modelo.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender='employees.NovedadNomina')
def notificar_novedad_aprobada_o_rechazada(sender, instance, created, **kwargs):
    """Notifica al coordinador que registró la novedad cuando cambia el estado
    de aprobación a aprobada o rechazada."""
    if created or instance.estado_aprobacion == 'pendiente':
        return
    registrado_por = instance.registrado_por
    if registrado_por is None or registrado_por.usuario is None:
        return

    try:
        from .push_utils import send_push
    except ImportError:
        return

    if instance.estado_aprobacion == 'aprobada':
        titulo = 'Novedad aprobada'
        cuerpo = (
            f'Tu novedad de {instance.empleado.nombre_completo} '
            f'({instance.get_tipo_display()}, {instance.fecha:%d/%m}) fue aprobada.'
        )
    elif instance.estado_aprobacion == 'rechazada':
        titulo = 'Novedad rechazada'
        motivo = (instance.motivo_rechazo or '').strip()
        cuerpo = (
            f'Tu novedad de {instance.empleado.nombre_completo} '
            f'({instance.get_tipo_display()}, {instance.fecha:%d/%m}) fue rechazada.'
            + (f' Motivo: {motivo[:80]}' if motivo else '')
        )
    else:
        return

    try:
        send_push(
            registrado_por.usuario, titulo, cuerpo,
            url='/reportes/novedades/semana/',
            tag=f'novedad-{instance.pk}',
            tag_group='novedades',  # agrupa varias novedades bajo un tipo
            actions=[
                {'action': 'ver', 'title': 'Ver semana'},
            ],
            action_urls={'ver': '/reportes/novedades/semana/'},
        )
    except Exception as e:
        logger.error(f'Fallo notificando novedad {instance.pk}: {e}')


@receiver(post_save, sender='employees.AsistenciaDiaria')
def notificar_ausencia_registrada(sender, instance, created, **kwargs):
    """Notifica al empleado cuando su jefe registra una ausencia (cualquier
    estado que no sea 'presente')."""
    if instance.estado == 'presente':
        return
    if instance.empleado is None or instance.empleado.usuario is None:
        return
    # No notificar cuando el propio empleado marca su asistencia
    if instance.registrado_por and instance.registrado_por.usuario_id == instance.empleado.usuario_id:
        return

    try:
        from .push_utils import send_push
    except ImportError:
        return

    etiqueta = instance.get_estado_display()
    cuerpo = f'Tu jefe registró tu asistencia del {instance.fecha:%d/%m} como "{etiqueta}".'
    if instance.motivo:
        cuerpo += f' Motivo: {instance.motivo[:80]}'
    try:
        send_push(
            instance.empleado.usuario,
            'Asistencia registrada', cuerpo,
            url='/empleados/mi-perfil/',
            tag=f'asistencia-{instance.pk}',
            tag_group='asistencia',
        )
    except Exception as e:
        logger.error(f'Fallo notificando ausencia {instance.pk}: {e}')
