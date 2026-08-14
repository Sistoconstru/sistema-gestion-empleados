"""Marca automáticamente los cargos GERENTE y DIRECTOR * como excluidos del
control de asistencia. Idempotente: solo toca los que aún no están marcados.
"""
from django.db import migrations


def marcar_excluidos(apps, schema_editor):
    Cargo = apps.get_model('organizational', 'Cargo')
    # Empieza por 'GERENTE' o 'DIRECTOR' (case-insensitive)
    filas = Cargo.objects.filter(
        nombre__iregex=r'^(GERENTE|DIRECTOR)',
        excluido_control_asistencia=False,
    )
    n = filas.count()
    filas.update(excluido_control_asistencia=True)
    print(f'  → {n} cargo(s) marcados como excluidos del control de asistencia.')


def desmarcar(apps, schema_editor):
    Cargo = apps.get_model('organizational', 'Cargo')
    Cargo.objects.filter(nombre__iregex=r'^(GERENTE|DIRECTOR)').update(
        excluido_control_asistencia=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('organizational', '0012_excluido_control_asistencia'),
    ]

    operations = [
        migrations.RunPython(marcar_excluidos, desmarcar),
    ]
