from django.db import migrations


TIPOS = [
    {
        'codigo': 'vacacion_aprobada',
        'nombre': 'Vacación aprobada por RRHH',
        'descripcion': 'RRHH aprobó una solicitud de vacaciones desde Odoo.',
        'plantilla_titulo': 'Tu solicitud de vacaciones fue aprobada',
        'plantilla_mensaje': (
            'RRHH aprobó tu solicitud de vacaciones del {fecha_inicio} al {fecha_fin}. '
            'Recuerda coordinar la entrega de responsabilidades con tu equipo antes de tu ausencia.'
        ),
    },
    {
        'codigo': 'vacacion_rechazada',
        'nombre': 'Vacación rechazada por RRHH',
        'descripcion': 'RRHH rechazó una solicitud de vacaciones desde Odoo.',
        'plantilla_titulo': 'Tu solicitud de vacaciones fue rechazada',
        'plantilla_mensaje': (
            'RRHH rechazó tu solicitud de vacaciones del {fecha_inicio} al {fecha_fin}. '
            'Motivo: {motivo}. Comunícate con tu jefe directo o RRHH para más detalles.'
        ),
    },
    {
        'codigo': 'vacacion_cancelada',
        'nombre': 'Vacación cancelada por RRHH',
        'descripcion': 'RRHH canceló una solicitud de vacaciones desde Odoo.',
        'plantilla_titulo': 'Tu solicitud de vacaciones fue cancelada',
        'plantilla_mensaje': (
            'RRHH canceló tu solicitud de vacaciones del {fecha_inicio} al {fecha_fin}. '
            'Comunícate con tu jefe directo o RRHH si necesitas más información.'
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
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_tipos, borrar_tipos),
    ]
