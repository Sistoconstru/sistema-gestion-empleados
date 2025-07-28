# apps/training/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.employees.models import HistorialCargo
from .utils import asignar_capacitaciones_por_cargo

@receiver(post_save, sender=HistorialCargo)
def asignar_capacitaciones_nuevo_cargo(sender, instance, created, **kwargs):
    """Asignar capacitaciones cuando se asigna un nuevo cargo"""
    if created and instance.activo:
        capacitaciones_asignadas = asignar_capacitaciones_por_cargo(instance.empleado)
        if capacitaciones_asignadas > 0:
            # Enviar notificación al empleado
            pass

