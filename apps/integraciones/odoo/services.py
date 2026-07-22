import logging

import requests
from django.conf import settings

from .models import OdooSyncFalla
from .serializers import OdooEmpleadoSerializer


logger = logging.getLogger(__name__)


def push_empleado_a_odoo(empleado, evento):
    """Envía un POST síncrono al webhook de Odoo con el empleado.

    Diseño en docs/INTEGRACION_ODOO.md §3.6 (Opción A aprobada):
    - Timeout corto (default 2s) para no bloquear la UI.
    - Cualquier excepción de red registra OdooSyncFalla; el pull horario reconcilia.
    - 4xx → error de contrato, OdooSyncFalla con detalle, no reintentar.
    - 5xx / timeout → OdooSyncFalla, el pull recupera.
    """
    webhook_url = getattr(settings, 'SIGHU_ODOO_WEBHOOK_URL', '')
    webhook_token = getattr(settings, 'SIGHU_ODOO_WEBHOOK_TOKEN', '')

    if not webhook_url or not webhook_token:
        logger.debug(
            "Push a Odoo deshabilitado: SIGHU_ODOO_WEBHOOK_URL/TOKEN no configurados."
        )
        return

    payload = {
        'evento': evento,
        'empleado': OdooEmpleadoSerializer(empleado).data,
    }
    timeout = getattr(settings, 'SIGHU_ODOO_PUSH_TIMEOUT', 2)

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Authorization': f'Token {webhook_token}'},
            timeout=timeout,
        )
    except (requests.Timeout, requests.ConnectionError) as exc:
        OdooSyncFalla.objects.create(
            empleado=empleado,
            evento=evento,
            motivo='timeout_o_conexion',
            detalle=str(exc)[:500],
        )
        return
    except requests.RequestException as exc:
        OdooSyncFalla.objects.create(
            empleado=empleado,
            evento=evento,
            motivo='request_exception',
            detalle=str(exc)[:500],
        )
        return

    if 200 <= response.status_code < 300:
        logger.info(
            "Push empleado %s evento=%s a Odoo OK (http=%d)",
            empleado.id, evento, response.status_code,
        )
        return

    OdooSyncFalla.objects.create(
        empleado=empleado,
        evento=evento,
        motivo='4xx_contrato' if 400 <= response.status_code < 500 else '5xx_odoo',
        detalle=response.text[:500],
        http_status=response.status_code,
    )


def _vacaciones_webhook_url():
    """Resuelve la URL del webhook de vacaciones.

    1) Si SIGHU_ODOO_WEBHOOK_VACACIONES_URL está definida, usarla.
    2) Si no, derivarla de SIGHU_ODOO_WEBHOOK_URL reemplazando '/empleado' por
       '/vacaciones' al final. Esto permite reutilizar la misma base sin
       duplicar configuración.
    """
    explicit = getattr(settings, 'SIGHU_ODOO_WEBHOOK_VACACIONES_URL', '')
    if explicit:
        return explicit
    base = getattr(settings, 'SIGHU_ODOO_WEBHOOK_URL', '') or ''
    if base.endswith('/empleado'):
        return base[:-len('/empleado')] + '/vacaciones'
    return ''


def enviar_vacacion_a_odoo(solicitud):
    """Envía una SolicitudVacacion al webhook de Odoo.

    Contrato en docs/INTEGRACION_ODOO_VACACIONES.md. Devuelve (ok, data) donde:
    - ok=True  → data trae al menos {'leave_id', 'dias', 'estado'}.
    - ok=False → data trae {'motivo': str} para mostrar al jefe.

    A diferencia de push_empleado_a_odoo, esta llamada es interactiva: el jefe
    espera la respuesta, por eso el timeout default es más largo (20s).
    Las fallas se registran en OdooSyncFalla con evento='vacacion_enviada'.
    """
    webhook_url = _vacaciones_webhook_url()
    webhook_token = getattr(settings, 'SIGHU_ODOO_WEBHOOK_TOKEN', '')

    if not webhook_url or not webhook_token:
        return False, {'motivo': 'Integración Odoo no configurada (URL/TOKEN).'}

    payload = {
        'sighu_uuid': str(solicitud.empleado.id),
        'fecha_inicio': solicitud.fecha_inicio.isoformat(),
        'fecha_fin': solicitud.fecha_fin.isoformat(),
        'aprobado_por': solicitud.jefe_solicitante.nombre_completo if solicitud.jefe_solicitante_id else '',
    }
    timeout = getattr(settings, 'SIGHU_ODOO_VACACIONES_TIMEOUT', 20)
    evento = 'vacacion'

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Authorization': f'Token {webhook_token}', 'Content-Type': 'application/json'},
            timeout=timeout,
        )
    except (requests.Timeout, requests.ConnectionError) as exc:
        OdooSyncFalla.objects.create(
            empleado=solicitud.empleado, evento=evento,
            motivo='timeout_o_conexion', detalle=str(exc)[:500],
        )
        return False, {'motivo': f'No se pudo contactar a Odoo: {exc}'}
    except requests.RequestException as exc:
        OdooSyncFalla.objects.create(
            empleado=solicitud.empleado, evento=evento,
            motivo='request_exception', detalle=str(exc)[:500],
        )
        return False, {'motivo': f'Error de transporte: {exc}'}

    try:
        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
    except ValueError:
        data = {}

    if response.status_code == 200 and data.get('status') == 'recibido':
        logger.info(
            "Vacación empleado=%s leave_id=%s OK", solicitud.empleado_id, data.get('leave_id'),
        )
        return True, data

    if response.status_code == 200 and data.get('status') == 'rechazado':
        # Rechazo por reglas de negocio — no es falla de transporte, no va a OdooSyncFalla.
        return False, {'motivo': data.get('motivo', 'Rechazado por Odoo sin motivo.')}

    OdooSyncFalla.objects.create(
        empleado=solicitud.empleado, evento=evento,
        motivo='4xx_contrato' if 400 <= response.status_code < 500 else '5xx_odoo',
        detalle=(response.text or '')[:500], http_status=response.status_code,
    )
    return False, {'motivo': data.get('error') or f'HTTP {response.status_code}'}


def _saldos_endpoint_url():
    """URL del endpoint GET de saldos de vacaciones expuesto por Odoo.

    1) Si SIGHU_ODOO_SALDOS_URL está definida, usarla.
    2) Si no, derivarla de SIGHU_ODOO_WEBHOOK_URL reemplazando '/empleado' por
       '/vacaciones/saldos'.
    """
    explicit = getattr(settings, 'SIGHU_ODOO_SALDOS_URL', '')
    if explicit:
        return explicit
    base = getattr(settings, 'SIGHU_ODOO_WEBHOOK_URL', '') or ''
    if base.endswith('/empleado'):
        return base[:-len('/empleado')] + '/vacaciones/saldos'
    return ''


def obtener_saldo_vacaciones_odoo(empleado):
    """Consulta a Odoo el saldo de vacaciones actual del empleado y lo persiste.

    GET <SIGHU_ODOO_SALDOS_URL>?sighu_uuid=<id>
    Auth: Token <SIGHU_ODOO_WEBHOOK_TOKEN> (el mismo que ya usa el push).

    Contrato de respuesta (definido con el dev de Odoo):
        {
          "fecha_corte": "2026-07-22",
          "saldos": [
            {"sighu_uuid": "…", "cedula": "…", "nombre": "…",
             "saldo_dias_disponibles": 12.5}
          ]
        }

    Retorna un dict con el resultado:
        {'ok': True,  'saldo': Decimal(...), 'fecha_corte': date}
        {'ok': False, 'motivo': 'timeout|http_500|no_configurado|no_encontrado'}

    Si la llamada tiene éxito, actualiza Empleado.saldo_vacaciones_dias y
    saldo_vacaciones_actualizado con la respuesta. Si falla, deja el último
    valor conocido intacto (fallback silencioso).
    """
    from decimal import Decimal
    from django.utils import timezone
    from apps.employees.models import Empleado

    url = _saldos_endpoint_url()
    token = getattr(settings, 'SIGHU_ODOO_WEBHOOK_TOKEN', '')

    if not url or not token:
        logger.debug("Consulta de saldo deshabilitada: SIGHU_ODOO_SALDOS_URL/TOKEN no configurados.")
        return {'ok': False, 'motivo': 'no_configurado'}

    timeout = getattr(settings, 'SIGHU_ODOO_SALDOS_TIMEOUT', 3)

    try:
        response = requests.get(
            url,
            params={'sighu_uuid': str(empleado.id)},
            headers={'Authorization': f'Token {token}'},
            timeout=timeout,
        )
    except requests.Timeout:
        logger.info(f"Saldo Odoo timeout para empleado {empleado.id}")
        return {'ok': False, 'motivo': 'timeout'}
    except requests.RequestException as e:
        logger.info(f"Saldo Odoo error transporte para empleado {empleado.id}: {e}")
        return {'ok': False, 'motivo': 'error_transporte'}

    if response.status_code != 200:
        logger.info(
            f"Saldo Odoo HTTP {response.status_code} para empleado {empleado.id}"
        )
        return {'ok': False, 'motivo': f'http_{response.status_code}'}

    try:
        data = response.json()
    except ValueError:
        logger.info(f"Saldo Odoo respuesta no-JSON para empleado {empleado.id}")
        return {'ok': False, 'motivo': 'respuesta_invalida'}

    saldos = data.get('saldos') or []
    # Con ?sighu_uuid=X esperamos 0 o 1 elementos
    if not saldos:
        return {'ok': False, 'motivo': 'no_encontrado'}

    registro = saldos[0]
    saldo_raw = registro.get('saldo_dias_disponibles')
    if saldo_raw is None:
        return {'ok': False, 'motivo': 'sin_saldo_en_respuesta'}

    try:
        saldo = Decimal(str(saldo_raw))
    except (ValueError, TypeError):
        return {'ok': False, 'motivo': 'saldo_no_numerico'}

    # Persistir saldo + fecha_corte (si viene)
    from datetime import date as _date
    fecha_corte_raw = data.get('fecha_corte')
    fecha_corte = None
    if fecha_corte_raw:
        try:
            fecha_corte = _date.fromisoformat(fecha_corte_raw)
        except (ValueError, TypeError):
            logger.info(f"fecha_corte inválida: {fecha_corte_raw!r}")

    updates = {
        'saldo_vacaciones_dias': saldo,
        'saldo_vacaciones_actualizado': timezone.now(),
    }
    if fecha_corte is not None:
        updates['saldo_vacaciones_fecha_corte'] = fecha_corte
    Empleado.objects.filter(pk=empleado.pk).update(**updates)

    return {'ok': True, 'saldo': saldo, 'fecha_corte': fecha_corte}
