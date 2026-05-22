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
