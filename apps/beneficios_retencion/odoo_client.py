"""Cliente HTTP hacia Odoo para el módulo de beneficios de retención.

Contrato del endpoint Odoo:
`POST /sighu_sync/webhook/beneficio_retencion`
Autenticación con `Authorization: Token <SIGHU_ODOO_TOKEN>`.

Idempotente por `tramite_uuid`: repetir la misma llamada con el mismo uuid
actualiza el mismo registro en Odoo (útil para reintentos y para revocación).

Los soportes van embebidos en base64. Máximo 10 MB por archivo según acuerdo.
"""
import base64
import json
import logging
from datetime import date, datetime
from decimal import Decimal

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class OdooBeneficioError(Exception):
    """Error transitorio o de validación al llamar a Odoo."""


MAX_SOPORTE_BYTES = 10 * 1024 * 1024


def _timeout_odoo():
    return getattr(settings, 'ODOO_HTTP_TIMEOUT', 30)


def _base_url():
    url = getattr(settings, 'ODOO_BASE_URL', None)
    if not url:
        raise OdooBeneficioError('ODOO_BASE_URL no configurado.')
    return url.rstrip('/')


def _token():
    tk = getattr(settings, 'SIGHU_ODOO_TOKEN', None)
    if not tk:
        raise OdooBeneficioError('SIGHU_ODOO_TOKEN no configurado.')
    return tk


def _leer_archivo_base64(fieldfile):
    """Lee un FileField y devuelve (bytes_b64, nombre, tamaño_original)."""
    fieldfile.open('rb')
    try:
        contenido = fieldfile.read()
    finally:
        fieldfile.close()
    if len(contenido) > MAX_SOPORTE_BYTES:
        raise OdooBeneficioError(
            f'Archivo {fieldfile.name} supera el máximo de 10 MB '
            f'(tamaño: {len(contenido)} bytes).'
        )
    return base64.b64encode(contenido).decode('ascii'), len(contenido)


def _serializar_soporte(soporte):
    b64, _ = _leer_archivo_base64(soporte.archivo)
    return {
        'nombre': soporte.nombre_original or soporte.archivo.name.split('/')[-1],
        'tipo_mime': soporte.tipo_mime or 'application/octet-stream',
        'contenido_base64': b64,
    }


def _build_payload(tramite, estado):
    """Arma el JSON para POST /sighu_sync/webhook/beneficio_retencion.

    `estado` es 'validado' o 'revocado' — Odoo solo acepta esos dos.
    """
    emp = tramite.empleado
    validador = tramite.validado_por
    validado_por_nombre = ''
    if validador:
        validado_por_nombre = validador.get_full_name() or validador.username

    payload = {
        'tramite_uuid': str(tramite.pk),
        'sighu_uuid': str(emp.pk),
        'numero_documento': emp.numero_documento,
        'tipo': tramite.tipo,
        'anio_aplicacion': tramite.anio_aplicacion,
        'periodo_certificado': tramite.periodo_certificado,
        'estado': estado,
        'validado_por': validado_por_nombre,
        'validado_el': (tramite.validado_el or date.today()).isoformat(),
        'observacion': tramite.observacion_rrhh or tramite.observacion_empleado or '',
    }

    if tramite.tipo == 'dependientes':
        payload['dependientes'] = []
        for dep in tramite.dependientes.all().prefetch_related('soportes'):
            payload['dependientes'].append({
                'nombre': dep.nombres,
                'numero_documento': dep.numero_documento,
                'parentesco': dep.parentesco,
                'causal': dep.causal,
                'soportes': [_serializar_soporte(s) for s in dep.soportes.all()],
            })
    else:
        if tramite.valor is None:
            raise OdooBeneficioError('valor requerido para este tipo de beneficio.')
        payload['valor'] = float(tramite.valor)
        payload['periodicidad'] = tramite.periodicidad or 'anual'

    # Soportes principales — obligatorios en 'validado', opcionales en 'revocado'.
    if estado == 'validado':
        soportes = list(tramite.soportes.all())
        if not soportes and tramite.tipo != 'dependientes':
            raise OdooBeneficioError('Al menos un soporte es obligatorio para validar.')
        payload['soportes'] = [_serializar_soporte(s) for s in soportes]
    else:
        payload['soportes'] = []

    return payload


def enviar_a_odoo(tramite, estado='validado'):
    """Envía el trámite a Odoo. Actualiza `tramite` en sitio con la respuesta.

    Devuelve la respuesta JSON de Odoo. Lanza OdooBeneficioError en error
    transitorio (5xx, timeout) o de validación (4xx). El caller decide si
    guarda `estado='error_envio_odoo'` para reintentar después.
    """
    from django.utils import timezone

    payload = _build_payload(tramite, estado)
    url = f'{_base_url()}/sighu_sync/webhook/beneficio_retencion'
    headers = {
        'Authorization': f'Token {_token()}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    try:
        resp = requests.post(url, headers=headers,
                             data=json.dumps(payload), timeout=_timeout_odoo())
    except requests.RequestException as exc:
        raise OdooBeneficioError(f'Fallo de red hacia Odoo: {exc}') from exc

    try:
        data = resp.json()
    except ValueError:
        data = {'raw': resp.text[:500]}

    if resp.status_code >= 500:
        raise OdooBeneficioError(f'Odoo respondió {resp.status_code}: {data}')
    if resp.status_code >= 400:
        # 4xx: no reintentable, pero guardamos la respuesta para diagnóstico.
        tramite.respuesta_odoo = data
        tramite.ultimo_error_odoo = (
            data.get('error') or data.get('detalle') or f'HTTP {resp.status_code}'
        )
        tramite.save(update_fields=['respuesta_odoo', 'ultimo_error_odoo',
                                    'fecha_actualizacion'])
        raise OdooBeneficioError(
            f'Odoo rechazó el trámite ({resp.status_code}): '
            f'{tramite.ultimo_error_odoo}'
        )

    # 200 OK
    tramite.respuesta_odoo = data
    tramite.enviado_a_odoo_el = timezone.now()
    tramite.ultimo_error_odoo = ''
    if data.get('odoo_id'):
        tramite.odoo_id = data['odoo_id']
    if data.get('aplica_desde'):
        try:
            tramite.aplica_desde = date.fromisoformat(data['aplica_desde'])
        except (TypeError, ValueError):
            pass
    if data.get('vence_el'):
        try:
            tramite.vence_el = date.fromisoformat(data['vence_el'])
        except (TypeError, ValueError):
            pass
    tramite.save(update_fields=[
        'respuesta_odoo', 'enviado_a_odoo_el', 'ultimo_error_odoo',
        'odoo_id', 'aplica_desde', 'vence_el', 'fecha_actualizacion',
    ])
    return data
