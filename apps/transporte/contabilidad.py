"""El cierre de gastos camino a la contabilidad de Odoo.

Toda la contabilidad de los vehículos vive en Odoo. SIGHU captura el gasto
donde ocurre —el conductor con el recibo en la mano— y lo entrega cuando
el jefe cierra la cuenta. El cierre es lo que viaja y no el gasto suelto,
por una razón: un gasto se puede corregir, rechazar o reasignar mientras
está abierto, y contabilizar algo que todavía puede cambiar obliga a
reversar asientos. Al cerrar queda sellado, y recién entonces es un
documento.

Dos cosas que el lado de Odoo tiene que tener claras:

- **Un mismo gasto llega dos veces.** La cuenta del conductor y la del
  vehículo son independientes y el gasto entra en las dos. El `gasto_id`
  es el mismo en ambos envíos, así que sirve para no contarlo doble. Lo
  que mueve plata es el cierre de conductor —es a él a quien se le paga—;
  el de vehículo responde cuánto cuesta operar ese carro.

- **No todo lo que viene es costo.** Una multa a cargo del conductor es
  algo que él debe, no un gasto de operación. Va marcada con
  `cuenta_como_costo: false` y sumada aparte en `total_deuda_conductor`.

El envío nunca bloquea el cierre: la cuenta se firma igual y lo que falle
se reintenta solo. Un cierre que Odoo rechaza a propósito no se reintenta
nunca, porque repetirlo da siempre lo mismo.
"""
import logging

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from .models import CierreGastos
from .odoo_client import (
    OdooConflictoError, OdooTransporteError, avisar_cierre_anulado,
    enviar_cierre_gastos,
)

logger = logging.getLogger(__name__)

# Timeout corto: se llama con el jefe mirando la pantalla después de
# apretar "cerrar cuenta". El cierre ya está guardado, así que si Odoo
# tarda no hay nada que esperar.
TIMEOUT_PANTALLA = 8

ENVIADO = 'enviado'
EN_COLA = 'en_cola'
RECHAZADO = 'rechazado'


# --- Lo que se le manda -------------------------------------------------

def _plata(valor):
    """Un monto como número, en pesos. Nunca None: cero es cero."""
    return float(valor or 0)


def _momento(cuando):
    """Un instante en ISO 8601 con el offset de Bogotá, como se acordó.

    En la base vive en UTC. Mandarlo así sería igual de correcto —el
    offset va explícito—, pero quien lea el payload para entender un
    descuadre lo va a leer en hora local, y una diferencia de cinco horas
    en una fecha de cierre es justo lo que hace dudar del dato.
    """
    return timezone.localtime(cuando).isoformat() if cuando else None


def url_recibo(gasto):
    """Enlace permanente al soporte del gasto, para que Odoo lo descargue.

    Es un enlace a SIGHU y no la URL de S3 a propósito: las del bucket van
    firmadas y caducan en una hora, y un soporte contable tiene que poder
    abrirse cuando lo pida la revisoría, no solo el día que se envió.

    Se arma sobre `SIGHU_URL_PUBLICA` porque acá no hay request del cual
    sacar el host: esto corre tanto desde una vista como desde el cron.
    """
    if not gasto.recibo:
        return None
    base = (getattr(settings, 'SIGHU_URL_PUBLICA', '') or '').rstrip('/')
    ruta = reverse('odoo-transporte-recibo-gasto', kwargs={'gasto_id': gasto.pk})
    return f'{base}{ruta}'


def _linea(gasto):
    """Un renglón del cierre: el gasto con todo lo que Odoo necesita de él."""
    linea = {
        'gasto_id': str(gasto.pk),
        'fecha': gasto.fecha.isoformat(),
        'tipo': gasto.tipo,
        'tipo_nombre': gasto.get_tipo_display(),
        'monto': _plata(gasto.monto),
        'descripcion': gasto.descripcion or '',
        'estado': gasto.estado,
        'cuenta_como_costo': gasto.cuenta_como_costo,
        'placa': gasto.vehiculo.placa if gasto.vehiculo_id else None,
        'vehiculo_odoo_id': gasto.vehiculo.odoo_id if gasto.vehiculo_id else None,
        'conductor_cedula': str(gasto.conductor.numero_documento),
        'kilometraje': gasto.kilometraje,
        'recibo_url': url_recibo(gasto),
    }

    # Solo en las multas, que es donde significa algo.
    if gasto.tipo == gasto.MULTA:
        linea['responsable'] = gasto.responsable

    # El servicio que causó el gasto, cuando fue por uno en particular. Es
    # lo que le permite a Odoo colgar el costo del viaje y no del mes.
    if gasto.servicio_id:
        linea['servicio'] = {
            'odoo_modelo': gasto.servicio.odoo_modelo,
            'odoo_id': gasto.servicio.odoo_id,
            'ref': gasto.servicio.ref or '',
        }

    if gasto.registrado_por_id:
        quien = gasto.registrado_por
        linea['registrado_por'] = quien.get_full_name() or quien.username
        linea['lo_registro_el_conductor'] = not gasto.lo_registro_otro

    return linea


def payload_cierre(cierre):
    """El cierre completo, como lo recibe Odoo.

    Las líneas van en el mismo envío y no en una consulta aparte: el valor
    del cierre es que sus renglones y su total se correspondan, y partirlo
    en dos llamadas abre la puerta a contabilizar un total cuyas líneas
    todavía no llegaron.
    """
    gastos = list(cierre.gastos().order_by('fecha', 'fecha_creacion'))
    quien = cierre.cerrado_por

    datos = {
        'cierre_id': str(cierre.pk),
        'ambito': cierre.ambito,
        'moneda': 'COP',
        'cerrado_en': _momento(cierre.fecha_cierre),
        'cerrado_por': ((quien.get_full_name() or quien.username)
                        if cierre.cerrado_por_id else ''),
        'desde': cierre.desde.isoformat() if cierre.desde else None,
        'hasta': cierre.hasta.isoformat() if cierre.hasta else None,
        'cantidad': cierre.cantidad,
        'total_costo': _plata(cierre.total_costo),
        'total_deuda_conductor': _plata(cierre.total_deuda),
        'observaciones': cierre.observaciones or '',
        'conductor': None,
        'vehiculo': None,
        'gastos': [_linea(g) for g in gastos],
    }

    # El sujeto va siempre con cédula o placa, no con el id de SIGHU: son
    # las llaves que Odoo ya usa en los otros endpoints.
    if cierre.conductor_id:
        datos['conductor'] = {
            'cedula': str(cierre.conductor.numero_documento),
            'nombre': cierre.conductor.nombre_completo,
        }
    if cierre.vehiculo_id:
        datos['vehiculo'] = {
            'placa': cierre.vehiculo.placa,
            'odoo_id': cierre.vehiculo.odoo_id,
        }
    return datos


def payload_anulacion(cierre):
    """El aviso de que un cierre ya enviado dejó de valer."""
    quien = cierre.anulado_por
    return {
        'cierre_id': str(cierre.pk),
        'ambito': cierre.ambito,
        'anulado_en': _momento(cierre.anulado_en),
        'anulado_por': ((quien.get_full_name() or quien.username)
                        if cierre.anulado_por_id else ''),
        'motivo': cierre.motivo_anulacion or '',
    }


# --- El envío -----------------------------------------------------------

def enviar(cierre, timeout=None):
    """Le manda el cierre a Odoo. Devuelve (resultado, detalle).

    Nunca levanta: quien llama ya guardó el cierre y esto es lo que sigue,
    no una condición para que el cierre exista.
    """
    try:
        respuesta = enviar_cierre_gastos(payload_cierre(cierre),
                                         timeout=timeout)
    except OdooConflictoError as e:
        CierreGastos.objects.filter(pk=cierre.pk).update(
            conflicto_odoo=True, ultimo_error=e.motivo[:300])
        registrar = logger.error if e.es_culpa_nuestra else logger.warning
        registrar('Odoo rechazó el cierre %s de %s (%s): %s',
                  cierre.pk, cierre.sujeto, e.status_code, e.motivo)
        return RECHAZADO, e.motivo
    except OdooTransporteError as e:
        CierreGastos.objects.filter(pk=cierre.pk).update(
            ultimo_error=str(e)[:300])
        logger.info('Cierre %s pendiente de enviar a Odoo: %s', cierre.pk, e)
        return EN_COLA, str(e)

    ref = _ref_de(respuesta)
    CierreGastos.objects.filter(pk=cierre.pk).update(
        sincronizado=True, fecha_sincronizacion=timezone.now(),
        odoo_ref=ref, ultimo_error='', conflicto_odoo=False)
    logger.info('Cierre %s de %s enviado a Odoo%s', cierre.pk, cierre.sujeto,
                f' como {ref}' if ref else '')
    return ENVIADO, ref


def enviar_anulacion(cierre, timeout=None):
    """Le avisa a Odoo que un cierre que ya le mandamos dejó de valer.

    Si el cierre nunca llegó no hay nada que avisar: no existe del otro
    lado y un aviso de anulación sobre algo que no está solo produciría un
    rechazo.
    """
    if not cierre.sincronizado:
        return EN_COLA, 'El cierre nunca llegó a Odoo; no hay nada que anular allá.'

    try:
        avisar_cierre_anulado(payload_anulacion(cierre), timeout=timeout)
    except OdooConflictoError as e:
        CierreGastos.objects.filter(pk=cierre.pk).update(
            conflicto_odoo_anulacion=True,
            ultimo_error_anulacion=e.motivo[:300])
        logger.warning('Odoo rechazó la anulación del cierre %s (%s): %s',
                       cierre.pk, e.status_code, e.motivo)
        return RECHAZADO, e.motivo
    except OdooTransporteError as e:
        CierreGastos.objects.filter(pk=cierre.pk).update(
            ultimo_error_anulacion=str(e)[:300])
        logger.info('Anulación del cierre %s pendiente de avisar: %s',
                    cierre.pk, e)
        return EN_COLA, str(e)

    CierreGastos.objects.filter(pk=cierre.pk).update(
        anulacion_sincronizada=True,
        fecha_sincronizacion_anulacion=timezone.now(),
        ultimo_error_anulacion='', conflicto_odoo_anulacion=False)
    logger.info('Anulación del cierre %s avisada a Odoo', cierre.pk)
    return ENVIADO, ''


def _ref_de(respuesta):
    """El documento que Odoo dice haber creado, si lo dice.

    Se guarda para que quien cerró la cuenta pueda buscarlo allá. Odoo
    todavía no definió con qué nombre lo devuelve, así que se aceptan los
    candidatos razonables y si no viene ninguno no pasa nada.
    """
    if not isinstance(respuesta, dict):
        return ''
    for llave in ('odoo_ref', 'ref', 'documento', 'move_name', 'name'):
        valor = respuesta.get(llave)
        if isinstance(valor, str) and valor.strip():
            return valor.strip()[:60]
    return ''


def pendientes():
    """Los cierres que tienen algo por mandarle a Odoo.

    Dos grupos en una sola consulta porque el reintento los trata igual:
    los activos que no han llegado, y los anulados que sí llegaron pero
    cuya anulación no. Los rechazados quedan fuera, que es el punto de
    marcarlos.
    """
    from django.db.models import Q

    return CierreGastos.objects.filter(
        Q(anulado_en__isnull=True, sincronizado=False, conflicto_odoo=False)
        | Q(anulado_en__isnull=False, sincronizado=True,
            anulacion_sincronizada=False, conflicto_odoo_anulacion=False)
    ).select_related('conductor', 'vehiculo', 'cerrado_por', 'anulado_por')
