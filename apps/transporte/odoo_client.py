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


# --- Para la fase de fletes ---------------------------------------------

def listar_viajes_pendientes(tipo=None, sede=None):
    """Traslados entre sedes, entregas de pedidos y recepciones de materia prima."""
    params = {}
    if tipo:
        params['tipo'] = tipo
    if sede:
        params['sede'] = sede
    datos = _pedir('GET', 'viajes_pendientes', params=params or None)
    if isinstance(datos, dict):
        datos = datos.get('viajes') or datos.get('results') or datos.get('data') or []
    return datos


def buscar_clientes(q):
    """Clientes aprobados para facturar, por NIT (con o sin dígito) o nombre."""
    datos = _pedir('GET', 'clientes', params={'q': q})
    if isinstance(datos, dict):
        datos = datos.get('clientes') or datos.get('results') or datos.get('data') or []
    return datos
