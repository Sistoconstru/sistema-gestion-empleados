"""Marca como cargos de conductor los que hoy conducen la flota.

Son los dos que ya tienen `requiere_licencia_conducir`: CONDUCTOR VENTAS y
CONDUCTOR VUELOS FORESTALES. Se marcan por código y no por el nombre ni por
ese flag, porque "requiere licencia" es un requisito del cargo y podría
aplicar mañana a alguien que no conduce la flota —un director que viaja,
por ejemplo— y entonces entraría al módulo sin que nadie lo decidiera.

Idempotente: solo toca los que aún no están marcados.
"""
from django.db import migrations

CODIGOS_CONDUCTOR = ['CCONVE', 'CCONBO']


def marcar(apps, schema_editor):
    Cargo = apps.get_model('organizational', 'Cargo')
    n = Cargo.objects.filter(
        codigo__in=CODIGOS_CONDUCTOR, es_cargo_conductor=False
    ).update(es_cargo_conductor=True)
    print(f'  → {n} cargo(s) marcados como cargo de conductor.')


def desmarcar(apps, schema_editor):
    Cargo = apps.get_model('organizational', 'Cargo')
    Cargo.objects.filter(codigo__in=CODIGOS_CONDUCTOR).update(
        es_cargo_conductor=False)


class Migration(migrations.Migration):

    dependencies = [
        ('organizational', '0016_cargo_es_cargo_conductor'),
    ]

    operations = [
        migrations.RunPython(marcar, desmarcar),
    ]
