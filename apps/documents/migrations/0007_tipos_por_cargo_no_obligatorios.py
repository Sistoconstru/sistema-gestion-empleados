"""Los tipos asignados a cargos dejan de ser obligatorios para todos.

"Certificado de alturas" (3 cargos de mecánico) y "Licencia de conducir"
(mensajero) estaban también marcados obligatorio=True a nivel general: a 273
de 274 empleados les figuraba faltando el de alturas y la subida múltiple lo
exigía a todos. Un tipo asignado por cargo lo exige su cargo; el "obligatorio"
general es para lo que deben tener todos.
"""
from django.db import migrations


def quitar_obligatorio_general(apps, schema_editor):
    TipoDocumentoEmpleado = apps.get_model('documents', 'TipoDocumentoEmpleado')
    TipoDocumentoCargo = apps.get_model('documents', 'TipoDocumentoCargo')
    por_cargo = TipoDocumentoCargo.objects.values_list('tipo_documento_id', flat=True)
    TipoDocumentoEmpleado.objects.filter(pk__in=por_cargo, obligatorio=True).update(obligatorio=False)


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0006_versiones_y_anexos'),
    ]

    operations = [
        migrations.RunPython(quitar_obligatorio_general, migrations.RunPython.noop),
    ]
