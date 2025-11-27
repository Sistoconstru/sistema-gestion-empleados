# Generated migration for adding product quantity and reservations

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0015_categoria_conversacion_mensaje_lecturaconversacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='cantidad_disponible',
            field=models.PositiveIntegerField(blank=True, help_text='Cantidad disponible del producto (NULL = sin límite)', null=True),
        ),
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, help_text='Fecha y hora de creación del registro')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, help_text='Fecha y hora de última actualización')),
                ('estado', models.CharField(choices=[('activa', 'Activa'), ('confirmada', 'Confirmada (Venta)'), ('cancelada', 'Cancelada')], default='activa', help_text='Estado de la reserva', max_length=15)),
                ('comprador', models.ForeignKey(help_text='Empleado que hizo la reserva', on_delete=django.db.models.deletion.CASCADE, related_name='reservas_como_comprador', to='employees.empleado')),
                ('creado_por', models.ForeignKey(help_text='Usuario que creó el registro', on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_creados', to='authentication.usuario')),
                ('producto', models.ForeignKey(help_text='Producto reservado', on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='employees.producto')),
                ('venta_asociada', models.OneToOneField(blank=True, help_text='Venta originada de esta reserva', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reserva_origen', to='employees.venta')),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'db_table': 'marketplace_reservas',
                'ordering': ['-fecha_creacion'],
            },
        ),
        migrations.AddIndex(
            model_name='reserva',
            index=models.Index(fields=['producto', 'estado'], name='marketplace__product_6789ab_idx'),
        ),
        migrations.AddIndex(
            model_name='reserva',
            index=models.Index(fields=['comprador', 'estado'], name='marketplace__comprad_4567cd_idx'),
        ),
        migrations.AddIndex(
            model_name='reserva',
            index=models.Index(fields=['fecha_creacion'], name='marketplace__fecha_c_2345ef_idx'),
        ),
        migrations.AddConstraint(
            model_name='reserva',
            constraint=models.UniqueConstraint(fields=['producto', 'comprador', 'estado'], name='reserva_unique_producto_comprador_estado'),
        ),
    ]
