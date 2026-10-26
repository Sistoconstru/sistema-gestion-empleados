"""Recalcula la vigencia de las publicaciones de empleados a 30 días.

La señal post_save les ponía 15 días a todas (y pisaba los 6 meses de la
publicación rápida). Se recalcula desde la fecha de creación para que todas
sigan la misma regla. Los anuncios no se tocan: vencen en su fecha_fin.

El valor de 30 va escrito aquí y no importado del modelo: una migración debe
seguir haciendo lo mismo aunque la constante cambie después.
"""
from datetime import timedelta

from django.db import migrations
from django.db.models import F


def recalcular(apps, schema_editor):
    Publicacion = apps.get_model('employees', 'Publicacion')
    Publicacion.objects.filter(es_anuncio=False).update(
        fecha_eliminacion_automatica=F('fecha_creacion') + timedelta(days=30)
    )


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0053_reaccion'),
    ]

    operations = [
        migrations.RunPython(recalcular, migrations.RunPython.noop),
    ]
