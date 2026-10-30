"""Estado borrador: Encuesta.fecha_publicacion.

Las encuestas que ya existen se publicaron al crearse, así que reciben su
fecha de creación y no pasan a borrador.
"""
from django.db import migrations, models
from django.db.models import F


def marcar_existentes_como_publicadas(apps, schema_editor):
    Encuesta = apps.get_model('surveys', 'Encuesta')
    Encuesta.objects.filter(fecha_publicacion__isnull=True).update(
        fecha_publicacion=F('fecha_creacion')
    )


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0004_opciones_si_no_faltantes'),
    ]

    operations = [
        migrations.AddField(
            model_name='encuesta',
            name='fecha_publicacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(marcar_existentes_como_publicadas, migrations.RunPython.noop),
    ]
