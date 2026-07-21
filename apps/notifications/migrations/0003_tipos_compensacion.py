from django.db import migrations


TIPOS = [
    {
        'codigo': 'vacacion_comp_aprobada',
        'nombre': 'Compensación de vacaciones aprobada',
        'descripcion': 'RRHH aplicó una compensación de vacaciones en dinero.',
        'plantilla_titulo': 'Compensación de vacaciones aprobada',
        'plantilla_mensaje': (
            'RRHH te aplicó una compensación de vacaciones en dinero por '
            '{dias} día(s), valor {valor}, en el lote de nómina del {fecha_lote}. '
            'Este pago se refleja en tu desprendible y descuenta de tu saldo de vacaciones.'
        ),
    },
    {
        'codigo': 'vacacion_comp_cancelada',
        'nombre': 'Compensación de vacaciones cancelada',
        'descripcion': 'RRHH revirtió una compensación de vacaciones previamente aplicada.',
        'plantilla_titulo': 'Compensación de vacaciones cancelada',
        'plantilla_mensaje': (
            'RRHH revirtió la compensación de vacaciones por {dias} día(s) '
            '(valor {valor}, lote {fecha_lote}). '
            'Los días vuelven a tu saldo disponible.'
        ),
    },
]


def crear_tipos(apps, schema_editor):
    TipoNotificacion = apps.get_model('notifications', 'TipoNotificacion')
    for t in TIPOS:
        TipoNotificacion.objects.update_or_create(
            codigo=t['codigo'],
            defaults={
                'nombre': t['nombre'],
                'descripcion': t['descripcion'],
                'plantilla_titulo': t['plantilla_titulo'],
                'plantilla_mensaje': t['plantilla_mensaje'],
                'enviar_email': False,
                'enviar_push': True,
                'activo': True,
            },
        )


def borrar_tipos(apps, schema_editor):
    TipoNotificacion = apps.get_model('notifications', 'TipoNotificacion')
    TipoNotificacion.objects.filter(codigo__in=[t['codigo'] for t in TIPOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_tipos_vacaciones'),
    ]

    operations = [
        migrations.RunPython(crear_tipos, borrar_tipos),
    ]
