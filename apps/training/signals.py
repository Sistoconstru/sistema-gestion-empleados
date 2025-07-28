# apps/training/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.employees.models import HistorialCargo
from .utils import asignar_capacitaciones_por_cargo
from apps.authentication.models import Usuario

@receiver(post_save, sender=HistorialCargo)
def asignar_capacitaciones_nuevo_cargo(sender, instance, created, **kwargs):
    """Asignar capacitaciones cuando se asigna un nuevo cargo"""
    if created and instance.activo:
        usuario_sistema = Usuario.objects.filter(is_superuser=True).first()
        capacitaciones_asignadas = asignar_capacitaciones_por_cargo(instance.empleado, usuario_sistema)
        if capacitaciones_asignadas > 0:
            # Enviar notificación al empleado
            pass

