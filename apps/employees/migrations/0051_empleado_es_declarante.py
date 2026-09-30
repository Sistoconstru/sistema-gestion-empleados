"""Marca de empleado declarante de renta.

Habilita el módulo de beneficios de retención en la fuente. El empleado la
marca desde su perfil (modal '¿Eres declarante?'). RRHH puede desmarcarla
desde admin si el status del empleado cambia.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0050_empleado_motivo_retiro'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='es_declarante',
            field=models.BooleanField(
                default=False,
                help_text='El empleado declaró estar obligado a presentar renta.',
            ),
        ),
    ]
