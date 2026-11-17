"""Cliente HTTP hacia Odoo para el módulo de transporte.

Odoo es el dueño del maestro de vehículos. SIGHU lo consulta y le avisa de
las asignaciones conductor-vehículo; los documentos y sus vencimientos son
de SIGHU y no viajan.

Endpoints, todos con `Authorization: Token <SIGHU_ODOO_WEBHOOK_TOKEN>`, el
mismo token saliente de empleados, vacaciones y beneficios:

    GET  /sighu_sync/vehiculos[?incluir_archivados=1]
    POST /sighu_sync/webhook/vehiculo_asignacion
    GET  /sighu_sync/viajes_pendientes
    GET  /sighu_sync/clientes?q=

Fechas sin hora en `YYYY-MM-DD`, y con hora en ISO 8601 con offset
explícito sobre America/Bogota, según lo acordado.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OdooTransporteError(Exception):
    """Falla al hablar con Odoo: red, autenticación o respuesta inesperada."""


class OdooConflictoError(OdooTransporteError):
    """Odoo rechazó el aviso a propósito (409), no por una falla.

    Significa que del lado de Odoo cambió algo —el coordinador reasignó el
    viaje, por ejemplo—, así que reintentar no sirve de nada: hay que
    mostrarle el motivo a quien lo marcó y parar.
    """

    def __init__(self, motivo, status_code=409):
        self.motivo = motivo
        self.status_code = status_code
        super().__init__(motivo)


def _motivo(resp):
    """El texto que Odoo da para rechazar, sin el envoltorio del JSON."""
    try:
        datos = resp.json()
    except ValueError:
        return (resp.text or '').strip()[:300] or 'Odoo no explicó el motivo.'
    if isinstance(datos, dict):
        for llave in ('detail', 'error', 'mensaje', 'message', 'motivo'):
            valor = datos.get(llave)
            if isinstance(valor, str) and valor.strip():
                return valor.strip()[:300]
    return str(datos)[:300]


def _timeout():
    return getattr(settings, 'SIGHU_ODOO_TRANSPORTE_TIMEOUT', 30)


def _base_url():
    """Raíz `/sighu_sync/` derivada de la URL de webhook ya configurada.

    Se deriva en vez de pedir una variable nueva, igual que hace el cliente
    de beneficios. `SIGHU_ODOO_WEBHOOK_URL` apunta al webhook de empleados,
    así que basta con quitarle esa cola.
    """
    explicita = getattr(settings, 'SIGHU_ODOO_TRANSPORTE_URL', '') or ''
    if explicita:
        return explicita.rstrip('/')

    base = (getattr(settings, 'SIGHU_ODOO_WEBHOOK_URL', '') or '').rstrip('/')
    if not base:
        raise OdooTransporteError(
            'No hay URL de Odoo configurada: definí SIGHU_ODOO_TRANSPORTE_URL '
            'o SIGHU_ODOO_WEBHOOK_URL.'
        )
    marca = '/sighu_sync/'
    if marca in base:
        return base[:base.index(marca) + len(marca)].rstrip('/')
    raise OdooTransporteError(
        f'No se pudo derivar la raíz de Odoo desde SIGHU_ODOO_WEBHOOK_URL '
        f'({base}). Definí SIGHU_ODOO_TRANSPORTE_URL.'
    )


def _headers():
    token = getattr(settings, 'SIGHU_ODOO_WEBHOOK_TOKEN', '') or ''
    if not token:
        raise OdooTransporteError('SIGHU_ODOO_WEBHOOK_TOKEN no está configurado.')
    return {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json',
    }


def _pedir(metodo, ruta, timeout=None, **kwargs):
    url = f'{_base_url()}/{ruta.lstrip("/")}'
    try:
        resp = requests.request(
            metodo, url, headers=_headers(),
            timeout=timeout or _timeout(), **kwargs)
    except requests.RequestException as e:
        raise OdooTransporteError(f'No se pudo contactar a Odoo ({url}): {e}') from e

    # Un 409 no es una falla: es Odoo diciendo que no, con un motivo. Se
    # separa del resto porque se trata al revés —no se reintenta— y lo que
    # importa es el texto, que va derecho a la pantalla del conductor.
    if resp.status_code == 409:
        raise OdooConflictoError(_motivo(resp))

    if resp.status_code >= 400:
        raise OdooTransporteError(
            f'Odoo respondió {resp.status_code} en {ruta}: {resp.text[:300]}')
    try:
        return resp.json()
    except ValueError as e:
        raise OdooTransporteError(
            f'Odoo devolvió algo que no es JSON en {ruta}: {resp.text[:200]}') from e


# --- Vehículos ----------------------------------------------------------

def listar_vehiculos(incluir_archivados=False):
    """Vehículos de la flota según Odoo.

    Devuelve la lista tal como la manda Odoo. Los archivados solo vienen si
    se piden, y traen `activo: false` y su fecha de baja.
    """
    params = {'incluir_archivados': 1} if incluir_archivados else None
    datos = _pedir('GET', 'vehiculos', params=params)
    # Odoo puede responder la lista directa o envuelta; se aceptan ambas
    # para no romper si cambia el envoltorio.
    if isinstance(datos, dict):
        datos = datos.get('vehiculos') or datos.get('results') or datos.get('data') or []
    if not isinstance(datos, list):
        raise OdooTransporteError(
            f'Se esperaba una lista de vehículos y llegó {type(datos).__name__}.')
    return datos


def avisar_asignacion(placa, cedula, desde, hasta=None, timeout=None):
    """Registra en Odoo que un conductor queda asignado a un vehículo.

    Odoo cierra sola la asignación anterior del conductor y es idempotente:
    repetir la misma llamada no duplica nada. Rechaza vehículos dados de
    baja y empleados inactivos, que es justo lo que queremos que valide
    quien es dueño del maestro.

    `desde` y `hasta` van como fecha sin hora (YYYY-MM-DD).

    `timeout` corto cuando se llama mientras alguien espera: si Odoo no
    contesta, el aviso queda pendiente y se reintenta, pero quien guardó el
    vehículo no se puede quedar mirando la pantalla medio minuto.
    """
    cuerpo = {
        'placa': placa,
        'cedula': str(cedula),
        'desde': desde.isoformat() if hasattr(desde, 'isoformat') else desde,
    }
    if hasta:
        cuerpo['hasta'] = hasta.isoformat() if hasattr(hasta, 'isoformat') else hasta
    logger.info('Avisando a Odoo la asignación %s → %s desde %s',
                placa, cedula, cuerpo['desde'])
    return _pedir('POST', 'webhook/vehiculo_asignacion',
                  json=cuerpo, timeout=timeout)


# --- Servicios ----------------------------------------------------------

def listar_viajes_pendientes(tipo=None, sede=None, timeout=None):
    """Traslados entre sedes, entregas de pedidos y recepciones de materia prima.

    Cada uno trae `vehiculo_id` cuando Odoo ya le asignó vehículo, que es lo
    que permite mostrarle a cada conductor lo suyo. Viene envuelto en
    `results`; se aceptan las otras formas por si cambia el envoltorio.

    `timeout` corto cuando se llama desde una pantalla: el valor general es
    para tareas de fondo, no para alguien esperando.
    """
    params = {}
    if tipo:
        params['tipo'] = tipo
    if sede:
        params['sede'] = sede
    datos = _pedir('GET', 'viajes_pendientes',
                   params=params or None, timeout=timeout)
    if isinstance(datos, dict):
        datos = datos.get('results') or datos.get('viajes') or datos.get('data') or []
    if not isinstance(datos, list):
        raise OdooTransporteError(
            f'Se esperaba una lista de viajes y llegó {type(datos).__name__}.')
    return datos


def avisar_servicio_iniciado(servicio, timeout=None):
    """Le avisa a Odoo que el conductor salió a hacer un servicio.

    El endpoint todavía no existe del lado de Odoo: mientras tanto esto
    responde 404 y el inicio queda marcado para reintentar, que es justo lo
    que se quiere. El dato ya está guardado en SIGHU; el día que Odoo lo
    implemente se sincroniza solo, sin tocar código.

    Contrato propuesto, en la misma línea que `vehiculo_asignacion`:

        POST /sighu_sync/webhook/servicio_iniciado
        {
          "odoo_modelo": "stock.picking",
          "odoo_id": 385,
          "ref": "CAL/OUT/00060",
          "placa": "JYN 240",
          "cedula": "71391550",
          "iniciado_en": "2026-11-17T06:42:00-05:00",
          "kilometraje": 125400
        }

    Idempotente: repetir el mismo aviso responde 200 y no cambia nada.
    """
    cuerpo = {
        'odoo_modelo': servicio.odoo_modelo,
        'odoo_id': servicio.odoo_id,
        'ref': servicio.ref,
        'placa': servicio.vehiculo.placa,
        'cedula': str(servicio.conductor.numero_documento),
        'iniciado_en': servicio.iniciado_en.isoformat(),
    }
    if servicio.kilometraje is not None:
        cuerpo['kilometraje'] = servicio.kilometraje
    logger.info('Avisando a Odoo la salida de %s (%s)',
                servicio.ref or servicio.odoo_id, servicio.vehiculo.placa)
    return _pedir('POST', 'webhook/servicio_iniciado',
                  json=cuerpo, timeout=timeout)


def avisar_servicio_finalizado(servicio, timeout=None):
    """Le avisa a Odoo que el conductor cerró el servicio.

    El formato y el nombre son los que propuso Odoo. SIGHU le dice
    "entrega" de cara al conductor, que es su palabra, y traduce aquí:
    esta función es la frontera entre los dos vocabularios.

        POST /sighu_sync/webhook/servicio_finalizado
        {
          "odoo_modelo": "stock.picking",
          "odoo_id": 385,
          "ref": "CAL/OUT/00060",
          "placa": "JYN 240",
          "cedula": "71391550",
          "iniciado_en": "2026-11-17T06:42:00-05:00",
          "finalizado_en": "2026-11-17T09:15:00-05:00",
          "kilometraje": 125620,
          "toneladas_entregadas": 0.519,
          "novedad": "sin_novedad",
          "observacion": ""
        }

    Las toneladas son soporte, no base de cobro: el valor lo calcula Odoo
    con su propio documento y usa esto para contrastar.
    """
    cuerpo = {
        'odoo_modelo': servicio.odoo_modelo,
        'odoo_id': servicio.odoo_id,
        'ref': servicio.ref,
        'placa': servicio.vehiculo.placa,
        'cedula': str(servicio.conductor.numero_documento),
        'iniciado_en': servicio.iniciado_en.isoformat(),
        'finalizado_en': servicio.entregado_en.isoformat(),
        'novedad': servicio.novedad,
        'observacion': servicio.observacion,
    }
    if servicio.kilometraje_llegada is not None:
        cuerpo['kilometraje'] = servicio.kilometraje_llegada
    if servicio.toneladas_entregadas is not None:
        cuerpo['toneladas_entregadas'] = float(servicio.toneladas_entregadas)
    logger.info('Avisando a Odoo el cierre de %s (%s), novedad=%s',
                servicio.ref or servicio.odoo_id, servicio.vehiculo.placa,
                servicio.novedad)
    return _pedir('POST', 'webhook/servicio_finalizado',
                  json=cuerpo, timeout=timeout)


def buscar_clientes(q):
    """Clientes aprobados para facturar, por NIT (con o sin dígito) o nombre.

    Hoy ninguna pantalla lo usa: los servicios se crean en Odoo, que ya sabe
    a quién le cobra. Se deja porque es el endpoint que haría falta si algún
    día SIGHU tuviera que registrar un flete externo por su cuenta.
    """
    datos = _pedir('GET', 'clientes', params={'q': q})
    if isinstance(datos, dict):
        datos = datos.get('clientes') or datos.get('results') or datos.get('data') or []
    return datos
