"""Avisa a Odoo cuando cambia el conductor de un vehículo.

Se intenta en el momento, porque lo normal es que Odoo esté arriba y así el
cambio queda registrado de una vez. Si falla, el vehículo queda marcado con
`asignacion_sincronizada=False` y el comando `sincronizar_vehiculos` lo
reintenta: un corte de red no puede dejar la asignación viviendo solo en
SIGHU sin que nadie se entere.

El aviso nunca interrumpe el guardado. Quien asigna un conductor está
haciendo un cambio en SIGHU; que Odoo no conteste en ese instante no es
razón para perderle el trabajo.
"""
import logging

from django.conf import settings
from django.db.models.signals import post_init, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Vehiculo
from .odoo_client import OdooTransporteError, avisar_asignacion

logger = logging.getLogger(__name__)


@receiver(post_init, sender=Vehiculo)
def _recordar_conductor(sender, instance, **kwargs):
    """Guarda el conductor con el que se leyó, para detectar el cambio."""
    instance._conductor_original = instance.conductor_id


@receiver(post_save, sender=Vehiculo)
def avisar_cambio_de_conductor(sender, instance, created, **kwargs):
    anterior = getattr(instance, '_conductor_original', None)
    instance._conductor_original = instance.conductor_id

    if not created and anterior == instance.conductor_id:
        return
    if not instance.conductor_id:
        # Quitar el conductor no se avisa: Odoo cierra la asignación sola
        # cuando llega la del siguiente. Avisar un "sin conductor" obligaría
        # a inventar una fecha de cierre que no tenemos.
        return

    desde = instance.asignacion_desde or timezone.localdate()
    try:
        avisar_asignacion(
            placa=instance.placa,
            cedula=instance.conductor.numero_documento,
            desde=desde,
            # Corto a propósito: hay alguien esperando a que termine de
            # guardar. Si Odoo tarda, se reintenta en la sincronización.
            timeout=getattr(settings, 'SIGHU_ODOO_ASIGNACION_TIMEOUT', 5),
        )
    except OdooTransporteError as e:
        logger.warning(
            'No se pudo avisar a Odoo la asignación de %s; queda pendiente: %s',
            instance.placa, e)
        Vehiculo.objects.filter(pk=instance.pk).update(
            asignacion_sincronizada=False,
            asignacion_desde=desde,
        )
        return
    except Exception as e:
        # Cualquier otra cosa tampoco debe tumbar el guardado.
        logger.exception('Error inesperado avisando la asignación de %s: %s',
                         instance.placa, e)
        Vehiculo.objects.filter(pk=instance.pk).update(
            asignacion_sincronizada=False, asignacion_desde=desde)
        return

    Vehiculo.objects.filter(pk=instance.pk).update(
        asignacion_sincronizada=True, asignacion_desde=desde)
