# apps/training/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.employees.models import HistorialCargo
from .utils import asignar_capacitaciones_por_cargo
from apps.authentication.models import Usuario
from .models import InscripcionCapacitacion
from .certificate_generator import CertificateGenerator
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=HistorialCargo)
def asignar_capacitaciones_nuevo_cargo(sender, instance, created, **kwargs):
    """Asignar capacitaciones cuando se asigna un nuevo cargo"""
    if created and instance.activo:
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        capacitaciones_asignadas = asignar_capacitaciones_por_cargo(instance.empleado, usuario_sistema)
        if capacitaciones_asignadas > 0:
            # Enviar notificación al empleado
            pass


@receiver(post_save, sender=InscripcionCapacitacion)
def auto_emitir_certificado(sender, instance, created, **kwargs):
    """Al aprobar la inscripción, asigna número y fecha de emisión del certificado.

    No genera PDF: el archivo se renderiza al vuelo en cada descarga (ver
    `descargar_certificado`). Externas no entran por aquí — su certificado lo
    sube RRHH manualmente y se sirve tal cual.
    """
    if instance.estado != 'aprobado':
        return
    if instance.capacitacion.es_externa():
        return
    if instance.numero_certificado and instance.fecha_emision_certificado:
        return  # Ya emitido; nada que hacer

    if not instance.puede_generar_certificado():
        logger.debug(
            f"Inscripción {instance.id} no cumple condiciones para emitir certificado "
            f"(estado: {instance.estado}, puntaje: {instance.puntaje_final})"
        )
        return

    try:
        CertificateGenerator.emitir_certificado(instance)
    except Exception as e:
        logger.error(
            f"Error en auto-emisión de certificado para inscripción {instance.id}: {e}"
        )

