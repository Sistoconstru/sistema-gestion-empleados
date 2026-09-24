"""Amplía max_length de NovedadNomina.tipo y separa dominical en diurno/nocturno.

Ley Colombia diferencia el recargo dentro del día festivo/domingo:
- dominical diurna (6am-7pm) → 100% recargo
- dominical nocturna (7pm-6am) → 150% recargo

Cambios:
1. Schema: max_length 25 → 32 y TIPO_CHOICES actualizado.
2. Datos: rename directo de los valores existentes:
   - 'hora_extra_dominical' → 'hora_extra_dominical_diurna'
   - 'recargo_dominical'    → 'recargo_dominical_diurno'

La reclasificación al tipo _nocturna/nocturno para las novedades que caen
en franja nocturna (00-06 y 19-24) se hace después con el management
command `reclasificar_dominicales_nocturnos --apply` (solo actúa sobre
las que tienen rango horario en franja nocturna).
"""
from django.db import migrations, models


def _rename_dominicales(apps, schema_editor):
    NovedadNomina = apps.get_model('employees', 'NovedadNomina')
    NovedadNomina.objects.filter(tipo='hora_extra_dominical').update(
        tipo='hora_extra_dominical_diurna'
    )
    NovedadNomina.objects.filter(tipo='recargo_dominical').update(
        tipo='recargo_dominical_diurno'
    )


def _revert_dominicales(apps, schema_editor):
    NovedadNomina = apps.get_model('employees', 'NovedadNomina')
    NovedadNomina.objects.filter(tipo='hora_extra_dominical_diurna').update(
        tipo='hora_extra_dominical'
    )
    NovedadNomina.objects.filter(tipo='hora_extra_dominical_nocturna').update(
        tipo='hora_extra_dominical'
    )
    NovedadNomina.objects.filter(tipo='recargo_dominical_diurno').update(
        tipo='recargo_dominical'
    )
    NovedadNomina.objects.filter(tipo='recargo_dominical_nocturno').update(
        tipo='recargo_dominical'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0046_empleado_fecha_retiro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='novedadnomina',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('hora_extra_diurna', 'Hora extra diurna'),
                    ('hora_extra_nocturna', 'Hora extra nocturna'),
                    ('hora_extra_dominical_diurna', 'Hora extra dominical/festivo diurna'),
                    ('hora_extra_dominical_nocturna', 'Hora extra dominical/festivo nocturna'),
                    ('recargo_nocturno', 'Recargo nocturno'),
                    ('recargo_dominical_diurno', 'Recargo dominical/festivo diurno'),
                    ('recargo_dominical_nocturno', 'Recargo dominical/festivo nocturno'),
                    ('vigilancia', 'Vigilancia'),
                ],
                max_length=32,
            ),
        ),
        migrations.RunPython(_rename_dominicales, _revert_dominicales),
    ]
