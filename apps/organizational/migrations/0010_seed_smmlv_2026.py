"""Siembra el SMMLV 2026 = $1.423.500. Idempotente — usa update_or_create
para no duplicar si ya existe.
"""
from django.db import migrations
from decimal import Decimal


def seed_smmlv(apps, schema_editor):
    Salario = apps.get_model('organizational', 'SalarioMinimoAnual')
    Salario.objects.update_or_create(
        year=2026,
        defaults={
            'valor': Decimal('1423500'),
            'decreto': 'Decreto 1435 de 2025',
            'observaciones': 'Sembrado en migración inicial.',
        },
    )


def unseed_smmlv(apps, schema_editor):
    Salario = apps.get_model('organizational', 'SalarioMinimoAnual')
    Salario.objects.filter(year=2026).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('organizational', '0009_salario_minimo_anual'),
    ]

    operations = [
        migrations.RunPython(seed_smmlv, unseed_smmlv),
    ]
