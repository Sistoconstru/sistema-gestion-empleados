"""Backfill de los trámites que quedaron con el estado eliminado `error_envio_odoo`.

La migración 0003 sacó ese estado del catálogo, pero los registros creados
antes se quedaron con el valor viejo en la BD y dejaron de renderizar en los
templates (ninguna rama coincidía, así que la columna Estado salía vacía).

Semánticamente esos trámites SÍ fueron validados por RRHH; lo único que
falló fue el envío a Odoo, que ya queda registrado en `ultimo_error_odoo`.
Por eso pasan a `validado`: la property `sync_odoo_pendiente` los va a
seguir marcando como pendientes de sincronizar.
"""
from django.db import migrations


ESTADO_VIEJO = 'error_envio_odoo'


def a_validado(apps, schema_editor):
    Tramite = apps.get_model('beneficios_retencion', 'TramiteBeneficio')
    Tramite.objects.filter(estado=ESTADO_VIEJO).update(estado='validado')


def revertir(apps, schema_editor):
    """Devuelve a `error_envio_odoo` solo los validados que nunca llegaron a Odoo."""
    Tramite = apps.get_model('beneficios_retencion', 'TramiteBeneficio')
    Tramite.objects.filter(
        estado='validado', enviado_a_odoo_el__isnull=True,
    ).exclude(ultimo_error_odoo='').update(estado=ESTADO_VIEJO)


class Migration(migrations.Migration):

    dependencies = [
        ('beneficios_retencion', '0003_alter_tramitebeneficio_estado'),
    ]

    operations = [
        migrations.RunPython(a_validado, revertir),
    ]
