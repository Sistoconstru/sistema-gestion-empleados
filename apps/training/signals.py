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
def auto_generar_certificado(sender, instance, created, **kwargs):
    """
    Genera automáticamente el certificado PDF cuando:
    - El estado cambia a 'aprobado'
    - Es una capacitación INTERNA (NO externa)
    - Cumple con la nota mínima
    - No tiene certificado generado previamente
    - La capacitación tiene plantilla de certificado

    IMPORTANTE: Las capacitaciones externas NO generan certificados automáticos
    porque el empleado presenta el certificado del proveedor externo.
    """
    # Solo generar si el estado es 'aprobado'
    if instance.estado == 'aprobado':
        # VALIDACIÓN CRÍTICA: NO generar certificado si es capacitación externa
        if instance.capacitacion.es_externa():
            logger.debug(
                f"Inscripción {instance.id} es de capacitación externa - "
                f"NO se genera certificado automático. "
                f"El certificado debe ser proporcionado por el proveedor externo."
            )
            return

        # Verificar si ya tiene certificado generado
        if not instance.certificado_generado:
            # Verificar que puede generar
            if instance.puede_generar_certificado():
                logger.info(
                    f"Generando certificado automático para inscripción {instance.id} "
                    f"(Empleado: {instance.empleado.nombre_completo}, "
                    f"Capacitación: {instance.capacitacion.nombre})"
                )
                try:
                    resultado = CertificateGenerator.generar_certificado(instance)
                    if resultado:
                        logger.info(f"Certificado generado exitosamente para inscripción {instance.id}")
                    else:
                        logger.warning(f"No se pudo generar certificado para inscripción {instance.id}")
                except Exception as e:
                    logger.error(f"Error en auto-generación de certificado para inscripción {instance.id}: {str(e)}")
            else:
                logger.debug(
                    f"Inscripción {instance.id} no cumple condiciones para generar certificado "
                    f"(Estado: {instance.estado}, Puntaje: {instance.puntaje_final})"
                )

