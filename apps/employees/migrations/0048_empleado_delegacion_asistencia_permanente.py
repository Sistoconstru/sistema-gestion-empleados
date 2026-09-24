"""Bypass del umbral de 30 subalternos para delegación permanente de asistencia.

Uso: RRHH lo activa manualmente en el admin para jefes con equipo pequeño
que necesitan delegar de forma permanente en su encargado_asistencia.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0047_novedad_tipos_dominical_split'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='delegacion_asistencia_permanente',
            field=models.BooleanField(
                default=False,
                help_text='Permite al encargado de asistencia registrar todos los días sin importar el tamaño del equipo (uso excepcional autorizado por RRHH).',
            ),
        ),
    ]
