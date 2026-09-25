"""Trazabilidad separada para la descarga de carta de vacaciones hecha por RRHH.

No pisa `carta_descargada_fecha` (que certifica que el empleado se dio por
enterado); registra en campos aparte cuándo y quién de RRHH la descargó.
"""
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0048_empleado_delegacion_asistencia_permanente'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitudvacacion',
            name='carta_descargada_rrhh_fecha',
            field=models.DateTimeField(
                blank=True, null=True,
                help_text='Fecha/hora de la última descarga hecha por RRHH.',
            ),
        ),
        migrations.AddField(
            model_name='solicitudvacacion',
            name='carta_descargada_rrhh_por',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='cartas_vacaciones_descargadas',
                to=settings.AUTH_USER_MODEL,
                help_text='Usuario RRHH que hizo la última descarga.',
            ),
        ),
    ]
