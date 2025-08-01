# =============================================================================
# apps/documents/signals.py - SEÑALES PARA AUTOMATIZACIÓN
# =============================================================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
import logging

from .models import DocumentoEmpleado
from apps.employees.models import Empleado, HistorialCargo

logger = logging.getLogger(__name__)

# Señal que se ejecuta cuando se sube un documento nuevo
@receiver(post_save, sender=DocumentoEmpleado)
def documento_uploaded(sender, instance, created, **kwargs):
    """Ejecutar acciones cuando se sube un documento"""
    if created:
        logger.info(f'Documento {instance.tipo_documento.nombre} subido por {instance.empleado.nombre_completo}')
        
        # Verificar si el empleado puede cambiar de estado
        from .views import verificar_cambio_estado_empleado
        verificar_cambio_estado_empleado(instance.empleado)

# Señal que se ejecuta cuando se aprueba un documento
@receiver(post_save, sender=DocumentoEmpleado)
def documento_approved(sender, instance, created, **kwargs):
    """Ejecutar acciones cuando se aprueba un documento"""
    if not created and instance.estado_aprobacion == 'aprobado' and instance.fecha_aprobacion:
        logger.info(f'Documento {instance.tipo_documento.nombre} aprobado para {instance.empleado.nombre_completo}')
        
        # Verificar cambio de estado del empleado
        from .views import verificar_cambio_estado_empleado
        verificar_cambio_estado_empleado(instance.empleado)

# Señal que se ejecuta cuando cambia el cargo de un empleado
@receiver(post_save, sender=HistorialCargo)
def cargo_changed(sender, instance, created, **kwargs):
    """Verificar documentos requeridos cuando cambia el cargo"""
    if created and instance.activo:
        logger.info(f'Cargo cambiado para {instance.empleado.nombre_completo}: {instance.cargo.nombre}')
        
        # Aquí se podría implementar lógica para notificar documentos adicionales requeridos
        # Por ahora solo logeamos el evento