from django.db import migrations


CODIGOS_HUERFANOS = ['ACTIVO', 'periodo_prueba', 'PRUEBA']

ESTADOS_NUEVOS = [
    {
        'codigo': 'LICENCIA',
        'nombre': 'Licencia/Incapacidad',
        'descripcion': 'Empleado en licencia o incapacidad. Conserva acceso al sistema.',
        'permite_acceso_sistema': True,
    },
    {
        'codigo': 'SUSPENDIDO',
        'nombre': 'Suspendido',
        'descripcion': 'Empleado suspendido temporalmente. Conserva acceso al sistema para gestiones.',
        'permite_acceso_sistema': True,
    },
    {
        'codigo': 'RETIRADO',
        'nombre': 'Retirado',
        'descripcion': 'Empleado retirado definitivamente. Sin acceso al sistema.',
        'permite_acceso_sistema': False,
    },
]


def consolidar_forward(apps, schema_editor):
    EstadoEmpleado = apps.get_model('employees', 'EstadoEmpleado')
    Empleado = apps.get_model('employees', 'Empleado')

    huerfanos = EstadoEmpleado.objects.filter(codigo__in=CODIGOS_HUERFANOS)
    for estado in huerfanos:
        empleados_asociados = Empleado.objects.filter(estado=estado).count()
        if empleados_asociados > 0:
            raise RuntimeError(
                f"Aborto: estado '{estado.codigo}' tiene {empleados_asociados} empleados asociados. "
                f"Reasignar manualmente al codigo canonico antes de re-correr esta migracion."
            )
    huerfanos.delete()

    for data in ESTADOS_NUEVOS:
        EstadoEmpleado.objects.get_or_create(
            codigo=data['codigo'],
            defaults={
                'nombre': data['nombre'],
                'descripcion': data['descripcion'],
                'permite_acceso_sistema': data['permite_acceso_sistema'],
            },
        )


def consolidar_backward(apps, schema_editor):
    EstadoEmpleado = apps.get_model('employees', 'EstadoEmpleado')
    Empleado = apps.get_model('employees', 'Empleado')

    codigos_nuevos = [d['codigo'] for d in ESTADOS_NUEVOS]
    nuevos = EstadoEmpleado.objects.filter(codigo__in=codigos_nuevos)
    for estado in nuevos:
        empleados_asociados = Empleado.objects.filter(estado=estado).count()
        if empleados_asociados > 0:
            raise RuntimeError(
                f"Aborto rollback: estado '{estado.codigo}' tiene {empleados_asociados} empleados asociados."
            )
    nuevos.delete()

    EstadoEmpleado.objects.bulk_create([
        EstadoEmpleado(codigo='ACTIVO', nombre='ACTIVO', permite_acceso_sistema=True),
        EstadoEmpleado(codigo='periodo_prueba', nombre='periodo_prueba', permite_acceso_sistema=True),
        EstadoEmpleado(codigo='PRUEBA', nombre='Per. de prueba', permite_acceso_sistema=True),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0024_add_cantidad_solicitada_to_reserva'),
    ]

    operations = [
        migrations.RunPython(consolidar_forward, consolidar_backward),
    ]
