# Generated migration for adding jefe_directo field to HistorialCargo

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0013_revert_activa_to_activo'),
    ]

    operations = [
        migrations.AddField(
            model_name='historialcargo',
            name='jefe_directo',
            field=models.ForeignKey(
                blank=True,
                help_text='Jefe directo del empleado (empleado que ocupa el cargo jefe)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='subordinados',
                to='employees.empleado',
            ),
        ),
    ]
