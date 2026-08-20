"""Siembra TipoPregunta 'CHECKMULT' (selección múltiple con checkboxes).

Complemento de PREGMULT (selección única). Aquí el empleado marca 0..N
opciones. Requiere el cambio de unique_together en surveys.RespuestaEncuesta
(migración paralela) para permitir varias filas por (participación, pregunta).

Idempotente vía update_or_create.
"""
from django.db import migrations


def seed(apps, schema_editor):
    TipoPregunta = apps.get_model('evaluations', 'TipoPregunta')
    TipoPregunta.objects.update_or_create(
        codigo='CHECKMULT',
        defaults={
            'nombre': 'Selección múltiple (checkboxes)',
            'descripcion': (
                'Pregunta con varias opciones donde el empleado puede marcar '
                'CERO, UNA o VARIAS. Se persiste una fila por opción elegida.'
            ),
            'permite_opciones': True,
            'permite_texto_libre': False,
        },
    )


def unseed(apps, schema_editor):
    TipoPregunta = apps.get_model('evaluations', 'TipoPregunta')
    TipoPregunta.objects.filter(codigo='CHECKMULT').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0015_seed_pregmult_seleccion_unica'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
