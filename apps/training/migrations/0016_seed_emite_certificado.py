"""Preserva la política previa: OBLIGATORIA e INDUCCION NO emitían certificado.

Antes el código bloqueaba esos tipos de forma hardcoded. Ahora la decisión
vive en `Capacitacion.emite_certificado`. Esta data migration deja las
existentes con esos tipos en False para no cambiar el comportamiento; RRHH
puede activarlas caso por caso desde el admin si lo necesitan (SST, etc.).
"""
from django.db import migrations


CODIGOS_SIN_CERTIFICADO = ['OBLIGATORIA', 'INDUCCION']


def desactivar_emite_para_obligatorias_e_induccion(apps, schema_editor):
    Capacitacion = apps.get_model('training', 'Capacitacion')
    actualizadas = Capacitacion.objects.filter(
        tipo__codigo__in=CODIGOS_SIN_CERTIFICADO
    ).update(emite_certificado=False)
    if actualizadas:
        print(f"  -> {actualizadas} capacitacion(es) tipo OBLIGATORIA/INDUCCION marcadas como emite_certificado=False")


def revertir(apps, schema_editor):
    """Backward: dejar todas en True (default del campo)."""
    Capacitacion = apps.get_model('training', 'Capacitacion')
    Capacitacion.objects.filter(
        tipo__codigo__in=CODIGOS_SIN_CERTIFICADO
    ).update(emite_certificado=True)


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0015_capacitacion_emite_certificado'),
    ]

    operations = [
        migrations.RunPython(desactivar_emite_para_obligatorias_e_induccion, revertir),
    ]
