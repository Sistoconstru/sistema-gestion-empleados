"""Aviso a los empleados cuando una encuesta pasa a activa.

El envío en sí vive en avisos.py. Aquí solo se detecta la transición a activa
(publicación o reactivación) y se lanza en segundo plano.

Antes el aviso se armaba aquí mismo y se disparaba al CREAR la encuesta. Eso
tenía dos fallos: avisaba de una encuesta todavía sin preguntas, y al crearla
desde el formulario la fecha_fin quedaba como texto en la instancia, el
formato %d/%m/%Y lanzaba ValueError y no salía ningún aviso. Así se quedaron
sin aviso la encuesta de beneficios (hasta que la reactivaron) y la de la
fiesta de fin de año. Ahora la encuesta nace como borrador y se avisa al
publicarla.
"""
import logging

from django.db import transaction
from django.db.models.signals import post_init, post_save
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


@receiver(post_init, sender='surveys.Encuesta')
def _recordar_estado_activa(sender, instance, **kwargs):
    """Guarda el valor de `activa` cargado desde BD para detectar transiciones."""
    instance._activa_anterior = instance.activa if instance.pk else None


@receiver(post_save, sender='surveys.Encuesta')
def _notificar_publicacion(sender, instance, created, **kwargs):
    """Avisa cuando la encuesta entra en estado activa.

    - created=True + activa=True → creada ya activa (p. ej. desde el admin).
    - antes False + ahora True → publicación o reactivación.
    Los que ya recibieron el aviso no lo reciben de nuevo (tag por usuario).
    Si aún no abre o no tiene preguntas, avisos.py no envía nada y el job de
    las 7:00 la avisa cuando corresponda.
    """
    antes = getattr(instance, '_activa_anterior', None)
    entro_en_activa = instance.activa and (created or antes is not True)
    instance._activa_anterior = instance.activa
    if not entro_en_activa:
        return

    from . import avisos
    from .models import Encuesta

    # Activada por fuera de "Publicar" (admin de Django): cuenta como publicada.
    if instance.fecha_publicacion is None:
        instance.fecha_publicacion = timezone.now()
        Encuesta.objects.filter(pk=instance.pk).update(fecha_publicacion=instance.fecha_publicacion)

    # on_commit: el hilo debe ver la encuesta ya guardada.
    transaction.on_commit(lambda: avisos.en_segundo_plano(avisos.avisar_publicacion, instance.pk))
