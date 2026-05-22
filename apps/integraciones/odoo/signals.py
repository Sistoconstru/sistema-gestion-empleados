from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.employees.models import Empleado, HistorialCargo

from .services import push_empleado_a_odoo


@receiver(post_save, sender=Empleado)
def _empleado_guardado(sender, instance, created, **kwargs):
    evento = 'created' if created else 'updated'
    transaction.on_commit(lambda: push_empleado_a_odoo(instance, evento))


@receiver(post_save, sender=HistorialCargo)
def _historial_cargo_guardado(sender, instance, created, **kwargs):
    if not instance.activo:
        return
    transaction.on_commit(lambda: push_empleado_a_odoo(instance.empleado, 'updated'))
