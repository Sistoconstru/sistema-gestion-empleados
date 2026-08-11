"""Marca automáticamente los cargos cuyo nombre empieza con 'APRENDIZ ' como
cargos de aprendiz SENA. Idempotente — solo toca los que aún no están marcados.
"""
from django.db import migrations


def marcar_cargos_aprendiz(apps, schema_editor):
    Cargo = apps.get_model('organizational', 'Cargo')
    actualizados = Cargo.objects.filter(
        nombre__istartswith='APRENDIZ',
        es_cargo_aprendiz=False,
    ).update(es_cargo_aprendiz=True)
    print(f'  → {actualizados} cargo(s) marcados como aprendiz SENA.')


def desmarcar_cargos_aprendiz(apps, schema_editor):
    Cargo = apps.get_model('organizational', 'Cargo')
    Cargo.objects.filter(nombre__istartswith='APRENDIZ').update(es_cargo_aprendiz=False)


class Migration(migrations.Migration):

    dependencies = [
        ('organizational', '0007_resolucion_sena_y_flag_aprendiz'),
    ]

    operations = [
        migrations.RunPython(marcar_cargos_aprendiz, desmarcar_cargos_aprendiz),
    ]
