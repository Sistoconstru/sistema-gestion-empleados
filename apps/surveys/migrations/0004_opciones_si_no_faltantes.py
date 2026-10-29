"""Da opciones "Sí" y "No" a las preguntas Sí/No que se crearon sin ellas.

Sin opciones, el formulario enviaba "si"/"no" y el guardado fallaba con un
500 (ver _asegurar_opciones_si_no en views.py). Afectaba a la encuesta
"ASISTENCIA FIESTA DE FIN DE AÑO 2026": nadie había podido enviarla.
"""
from django.db import migrations


def crear_opciones(apps, schema_editor):
    PreguntaEncuesta = apps.get_model('surveys', 'PreguntaEncuesta')
    OpcionEncuesta = apps.get_model('surveys', 'OpcionEncuesta')
    sin_opciones = PreguntaEncuesta.objects.filter(
        tipo_pregunta__codigo='SI_NO', opcionencuesta__isnull=True,
    )
    OpcionEncuesta.objects.bulk_create([
        OpcionEncuesta(pregunta=p, opcion=texto, valor_numerico=valor, orden=orden, activa=True)
        for p in sin_opciones
        for texto, valor, orden in (('Sí', 1, 1), ('No', 0, 2))
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0003_seed_tipos_encuesta'),
        ('evaluations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_opciones, migrations.RunPython.noop),
    ]
