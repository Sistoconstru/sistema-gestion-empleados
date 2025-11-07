# Generated manually to revert activa to activo field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0012_cambio_activo_a_activa_historialcargo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historialcargo',
            name='activa',
        ),
        migrations.AddField(
            model_name='historialcargo',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]