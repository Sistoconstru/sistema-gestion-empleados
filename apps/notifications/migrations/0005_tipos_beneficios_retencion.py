"""Tipos de notificación para beneficios de retención en la fuente."""
from django.db import migrations


TIPOS = [
    {
        'codigo': 'beneficio_ret_validado',
        'nombre': 'Beneficio de retención validado',
        'descripcion': 'RRHH validó un trámite de beneficio de retención.',
        'plantilla_titulo': 'Tu beneficio {tipo} fue validado — falta firmar la carta',
        'plantilla_mensaje': (
            'RRHH validó tu trámite de {tipo} para el año {anio_aplicacion}. '
            'Acércate a RRHH a firmar la carta juramentada para completar el proceso.'
        ),
    },
    {
        'codigo': 'beneficio_ret_rechazado',
        'nombre': 'Beneficio de retención rechazado',
        'descripcion': 'RRHH rechazó un trámite de beneficio de retención.',
        'plantilla_titulo': 'Tu beneficio {tipo} fue rechazado',
        'plantilla_mensaje': (
            'RRHH rechazó tu trámite de {tipo} para el año {anio_aplicacion}. '
            'Motivo: {motivo}. Puedes cargar un nuevo trámite corrigiendo los soportes.'
        ),
    },
    {
        'codigo': 'beneficio_ret_revocado',
        'nombre': 'Beneficio de retención revocado',
        'descripcion': 'RRHH revocó un beneficio previamente validado.',
        'plantilla_titulo': 'Tu beneficio {tipo} fue revocado',
        'plantilla_mensaje': (
            'RRHH revocó tu beneficio de {tipo} del año {anio_aplicacion}. '
            'Motivo: {motivo}. A partir de la próxima nómina, la deducción deja de aplicarse.'
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
        ('notifications', '0004_push_subscription'),
    ]

    operations = [
        migrations.RunPython(crear_tipos, borrar_tipos),
    ]
