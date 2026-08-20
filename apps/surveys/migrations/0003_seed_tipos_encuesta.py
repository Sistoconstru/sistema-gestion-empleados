"""Siembra tipos de encuesta comunes y limpia el tipo 'SMOKE' usado en tests.

Antes de esto el select "Tipo de Encuesta" en la pantalla de creación quedaba
vacío en producción, porque nunca se había sembrado ningún TipoEncuesta real.

Idempotente vía update_or_create.
"""
from django.db import migrations


TIPOS = [
    # (código, nombre, descripción, obligatoria, anónima, frecuencia_dias)
    ('CLIMA', 'Clima Organizacional',
     'Percepción del ambiente laboral, liderazgo y cultura interna. '
     'Se recomienda anónima para respuestas sinceras.',
     False, True, 365),
    ('SATISFAC', 'Satisfacción del Empleado',
     'Nivel de satisfacción del colaborador con su rol, equipo y beneficios.',
     False, True, 180),
    ('BIENESTAR', 'Bienestar y Salud Laboral',
     'Riesgos psicosociales, carga de trabajo y salud mental/física.',
     False, True, 365),
    ('ONBOARDING', 'Onboarding / Inducción',
     'Retroalimentación de nuevos ingresos sobre su proceso de inducción.',
     False, False, None),
    ('SALIDA', 'Encuesta de Salida',
     'Motivos de retiro voluntario y percepción del colaborador que se va.',
     False, False, None),
    ('CAPACITAC', 'Evaluación de Capacitación',
     'Retroalimentación posterior a una capacitación o entrenamiento.',
     False, False, None),
    ('LIDERAZGO', 'Evaluación de Liderazgo',
     'Feedback ascendente sobre el liderazgo directo. Se recomienda anónima.',
     False, True, 365),
    ('OTRO', 'Otro / General',
     'Encuestas puntuales que no encajan en las categorías anteriores.',
     False, False, None),
]


def seed(apps, schema_editor):
    TipoEncuesta = apps.get_model('surveys', 'TipoEncuesta')
    for codigo, nombre, desc, obl, anon, freq in TIPOS:
        TipoEncuesta.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'descripcion': desc,
                'obligatoria': obl,
                'anonima': anon,
                'frecuencia_dias': freq,
                'activo': True,
            },
        )
    # Limpiar el tipo de prueba SMOKE si quedó en la BD y no tiene encuestas
    Encuesta = apps.get_model('surveys', 'Encuesta')
    for t in TipoEncuesta.objects.filter(codigo='SMOKE'):
        if not Encuesta.objects.filter(tipo_encuesta=t).exists():
            t.delete()


def unseed(apps, schema_editor):
    TipoEncuesta = apps.get_model('surveys', 'TipoEncuesta')
    TipoEncuesta.objects.filter(codigo__in=[c for c, *_ in TIPOS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('surveys', '0002_respuesta_unique_por_opcion'),
    ]
    operations = [
        migrations.RunPython(seed, unseed),
    ]
