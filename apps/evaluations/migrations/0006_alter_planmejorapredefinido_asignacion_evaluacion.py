# Generated migration for adding related_name to PlanMejoraPredefinido

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluations', '0005_aumentar_periodo_evaluacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planmejorapredefinido',
            name='asignacion_evaluacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='planes_mejora', to='evaluations.asignacionevaluacion'),
        ),
    ]
