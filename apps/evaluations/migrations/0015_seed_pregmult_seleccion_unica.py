"""Siembra TipoPregunta 'PREGMULT' (selección única entre varias opciones).

Es el tipo clásico de encuesta con opciones a/b/c/d donde el empleado
elige UNA. El código y el resto de la app (surveys) ya lo referencian
en varios lugares; solo faltaba el registro en BD.

Idempotente vía update_or_create.
"""
from django.db import migrations


def seed(apps, schema_editor):
    TipoPregunta = apps.get_model('evaluations', 'TipoPregunta')
    TipoPregunta.objects.update_or_create(
        codigo='PREGMULT',
        defaults={
            'nombre': 'Selección única (varias opciones)',
            'descripcion': (
                'Pregunta con varias opciones (a, b, c, d…) donde el empleado '
                'elige exactamente UNA. Ideal para encuestas de opinión y '
                'preferencias.'
            ),
            'permite_opciones': True,
            'permite_texto_libre': False,
        },
    )


def unseed(apps, schema_editor):
    TipoPregunta = apps.get_model('evaluations', 'TipoPregunta')
    TipoPregunta.objects.filter(codigo='PREGMULT').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0014_actualizar_evaluaciones_desaprobadas'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
