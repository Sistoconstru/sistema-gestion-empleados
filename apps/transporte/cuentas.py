"""Las cuentas abiertas de gastos y su cierre.

Una "cuenta abierta" es simplemente lo que todavía no tiene cierre. No hay
períodos: el jefe corta cuando quiere, y lo que estaba abierto en ese
momento queda sellado con la llave del cierre.

La del conductor y la del vehículo son independientes. El mismo gasto entra
en las dos y cada una se cierra por su lado, porque responden preguntas
distintas: cuánto le debo a esta persona, y cuánto cuesta operar este carro.
"""
import logging

from django.db import transaction
from django.db.models import Count, Max, Min, Sum
from django.utils import timezone

from .models import CierreGastos, GastoVehiculo
from .permisos import conductores_a_cargo, conductores_vigentes, gastos_visibles

logger = logging.getLogger(__name__)


class CierreImposible(Exception):
    """No se puede cerrar todavía, y el mensaje dice por qué."""


def _campo_cierre(ambito):
    return ('cierre_conductor' if ambito == CierreGastos.CONDUCTOR
            else 'cierre_vehiculo')


def gastos_abiertos(ambito, sujeto_id, base=None):
    """Los gastos sin cerrar de esa cuenta.

    `base` acota al universo que el usuario puede ver; sin ella se mira
    todo, que es lo que hace falta al recalcular un cierre.
    """
    gastos = base if base is not None else GastoVehiculo.objects.all()
    filtro = {_campo_cierre(ambito) + '__isnull': True}
    if ambito == CierreGastos.CONDUCTOR:
        filtro['conductor_id'] = sujeto_id
    else:
        filtro['vehiculo_id'] = sujeto_id
    return gastos.filter(**filtro)


def _resumen(gastos):
    datos = gastos.aggregate(
        costo=Sum('monto', filter=GastoVehiculo.filtro_costo()),
        deuda=Sum('monto', filter=GastoVehiculo.filtro_deuda_conductor()),
        cantidad=Count('id'),
        desde=Min('fecha'),
        hasta=Max('fecha'),
    )
    return {
        'costo': datos['costo'] or 0,
        'deuda': datos['deuda'] or 0,
        'cantidad': datos['cantidad'] or 0,
        'desde': datos['desde'],
        'hasta': datos['hasta'],
        'pendientes': gastos.filter(estado=GastoVehiculo.PENDIENTE).count(),
    }


def cuentas_abiertas(usuario):
    """Lo que está sin cerrar, por conductor y por vehículo.

    Se listan también los que están en cero: que un conductor no tenga
    gastos abiertos es información, y si no aparece el jefe no sabe si es
    que no gastó o es que no lo está viendo.
    """
    from .permisos import empleado_de, vehiculos_visibles

    visibles = gastos_visibles(usuario)

    if usuario.is_staff:
        conductores = conductores_vigentes()
    else:
        conductores = conductores_a_cargo(empleado_de(usuario))

    por_conductor = []
    for empleado in conductores.order_by('apellidos', 'nombres'):
        abiertos = gastos_abiertos(CierreGastos.CONDUCTOR, empleado.pk, visibles)
        datos = _resumen(abiertos)
        datos.update({'ambito': CierreGastos.CONDUCTOR, 'sujeto': empleado,
                      'sujeto_id': empleado.pk})
        por_conductor.append(datos)

    por_vehiculo = []
    for vehiculo in vehiculos_visibles(usuario).order_by('placa'):
        abiertos = gastos_abiertos(CierreGastos.VEHICULO, vehiculo.pk, visibles)
        datos = _resumen(abiertos)
        datos.update({'ambito': CierreGastos.VEHICULO, 'sujeto': vehiculo,
                      'sujeto_id': vehiculo.pk})
        por_vehiculo.append(datos)

    return por_conductor, por_vehiculo


@transaction.atomic
def cerrar_cuenta(ambito, sujeto, usuario, observaciones='', base=None):
    """Cierra la cuenta y sella los gastos que estaban abiertos.

    Se vuelve a leer todo dentro de la transacción: entre que el jefe vio
    la pantalla y apretó el botón pudo entrar un gasto nuevo, y el total
    que se congela tiene que ser el de lo que realmente se selló.
    """
    campo = _campo_cierre(ambito)
    candidatos = list(
        gastos_abiertos(ambito, sujeto.pk, base).values_list('pk', flat=True))
    if not candidatos:
        raise CierreImposible('No hay gastos abiertos para cerrar.')

    # El bloqueo va sobre una consulta por id y no sobre la original:
    # `gastos_visibles` trae un DISTINCT —por el OR entre conductor y
    # vehículo— y Postgres no admite FOR UPDATE con DISTINCT. Tampoco se
    # puede agregar sobre el queryset bloqueado, así que primero se cierra
    # el candado listando los ids y después se suma sobre esos mismos.
    ids = list(GastoVehiculo.objects
               .select_for_update()
               .filter(pk__in=candidatos, **{campo + '__isnull': True})
               .values_list('pk', flat=True))
    if not ids:
        raise CierreImposible(
            'Esos gastos acaban de quedar cerrados en otra cuenta. '
            'Recarga la pantalla.')

    gastos = GastoVehiculo.objects.filter(pk__in=ids)
    datos = _resumen(gastos)

    if datos['pendientes']:
        raise CierreImposible(
            f'Hay {datos["pendientes"]} gasto(s) sin revisar en esta cuenta. '
            f'Cerrar con algo pendiente es cuadrar un total que todavía '
            f'puede cambiar de monto: apruébalos o recházalos primero.')

    cierre = CierreGastos.objects.create(
        ambito=ambito,
        conductor=sujeto if ambito == CierreGastos.CONDUCTOR else None,
        vehiculo=sujeto if ambito == CierreGastos.VEHICULO else None,
        total_costo=datos['costo'],
        total_deuda=datos['deuda'],
        cantidad=datos['cantidad'],
        desde=datos['desde'],
        hasta=datos['hasta'],
        cerrado_por=usuario,
        observaciones=observaciones.strip()[:2000],
    )

    GastoVehiculo.objects.filter(pk__in=ids).update(**{campo: cierre})

    logger.info('Cuenta de %s %s cerrada por %s: %s gastos, costo %s',
                ambito, cierre.sujeto, usuario, datos['cantidad'],
                datos['costo'])
    return cierre


@transaction.atomic
def anular_cierre(cierre, usuario, motivo):
    """Deshace un cierre y devuelve sus gastos a la cuenta abierta."""
    if not cierre.esta_activo:
        raise CierreImposible('Ese cierre ya estaba anulado.')
    if not (motivo or '').strip():
        raise CierreImposible(
            'Para anular un cierre hay que decir por qué: el total que '
            'quedó firmado deja de valer y tiene que constar la razón.')

    campo = _campo_cierre(cierre.ambito)
    GastoVehiculo.objects.filter(**{campo: cierre}).update(**{campo: None})

    cierre.anulado_en = timezone.now()
    cierre.anulado_por = usuario
    cierre.motivo_anulacion = motivo.strip()[:300]
    cierre.save(update_fields=['anulado_en', 'anulado_por', 'motivo_anulacion'])

    logger.info('Cierre %s anulado por %s: %s', cierre.pk, usuario, motivo[:120])
    return cierre
