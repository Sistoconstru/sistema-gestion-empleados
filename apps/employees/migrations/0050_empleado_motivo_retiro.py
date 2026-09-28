"""Motivo y observación del retiro, poblados desde el endpoint Odoo.

Odoo llama a `POST /api/v1/odoo/empleados/inactivar/` cuando RRHH registra la
fecha de terminación en el contrato; con esto SIGHU guarda el porqué del
retiro para consultarlo en admin y reportes.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0049_solicitud_vacacion_carta_rrhh'),
    ]

    operations = [
        migrations.AddField(
            model_name='empleado',
            name='motivo_retiro',
            field=models.CharField(
                blank=True, max_length=40,
                choices=[
                    ('terminacion_contrato', 'Terminación de contrato'),
                    ('vencimiento_termino_fijo', 'Vencimiento de término fijo'),
                    ('fin_aprendizaje', 'Fin de contrato de aprendizaje'),
                    ('otro', 'Otro'),
                ],
                help_text='Motivo del retiro registrado por RRHH (Odoo).',
            ),
        ),
        migrations.AddField(
            model_name='empleado',
            name='observacion_retiro',
            field=models.TextField(
                blank=True,
                help_text='Observación libre del retiro (Odoo).',
            ),
        ),
    ]
