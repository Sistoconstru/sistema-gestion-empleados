"""Marca automáticamente los cargos GERENTE * como excluidos de gestionar
asistencia (no ven el módulo, no reciben recordatorios, no se miden).
Los DIRECTOR * NO se marcan aquí — ellos sí gestionan la asistencia de
su equipo aunque a ellos no se les controle.
Idempotente: solo toca los que aún no están marcados.
"""
from django.db import migrations


def marcar_gerente(apps, schema_editor):
    Cargo = apps.get_model('organizational', 'Cargo')
    filas = Cargo.objects.filter(
        nombre__istartswith='GERENTE',
        excluido_gestion_asistencia=False,
    )
    n = filas.count()
    filas.update(excluido_gestion_asistencia=True)
    print(f'  → {n} cargo(s) GERENTE marcados como excluidos de gestión de asistencia.')


def desmarcar(apps, schema_editor):
    Cargo = apps.get_model('organizational', 'Cargo')
    Cargo.objects.filter(nombre__istartswith='GERENTE').update(
        excluido_gestion_asistencia=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('organizational', '0014_excluido_gestion_asistencia'),
    ]

    operations = [
        migrations.RunPython(marcar_gerente, desmarcar),
    ]
