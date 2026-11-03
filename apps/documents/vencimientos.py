"""Aviso de documentos por vencer (campana + push), a 30 y 7 días y el día del vencimiento.

Reemplaza al comando check_document_expiry (eliminado), que nunca se
programó: mandaba un correo en cada corrida, sin control de repetidos, y su
reporte a administradores usaba una plantilla que no existía.

Idempotente por (documento, umbral) vía push_tag: correr el job dos veces el
mismo día, o un día con el servidor caído y reiniciado, no repite avisos.
"""
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

UMBRALES_DIAS = (30, 7, 0)


def _avisar(usuario, tipo, titulo, cuerpo, url, tag, datos):
    from apps.notifications.models import Notificacion
    from apps.notifications.push_utils import send_push

    if Notificacion.objects.filter(usuario=usuario, datos_adicionales__contains={'push_tag': tag}).exists():
        return False
    Notificacion.objects.create(
        usuario=usuario, tipo_notificacion=tipo, titulo=titulo, mensaje=cuerpo,
        datos_adicionales={'push_tag': tag, **datos},
    )
    send_push(usuario, titulo, cuerpo, url=url, tag=tag, tag_group='documentos')
    return True


def avisar_vencimientos(hoy=None):
    from django.contrib.auth import get_user_model
    from apps.notifications.models import TipoNotificacion
    from .models import DocumentoEmpleado

    hoy = hoy or date.today()
    tipo, _ = TipoNotificacion.objects.get_or_create(
        codigo='documento_por_vencer',
        defaults={
            'nombre': 'Documento por vencer',
            'descripcion': 'Aviso de documentos con fecha de vencimiento cercana.',
            'plantilla_titulo': 'Documento por vencer',
            'plantilla_mensaje': 'Un documento está por vencer.',
            'enviar_email': False, 'enviar_push': True, 'activo': True,
        },
    )
    rrhh = list(get_user_model().objects.filter(is_staff=True, is_active=True))

    avisos = 0
    for dias in UMBRALES_DIAS:
        documentos = DocumentoEmpleado.objects.filter(
            estado_aprobacion='aprobado', fecha_vencimiento=hoy + timedelta(days=dias),
        ).select_related('empleado__usuario', 'tipo_documento')
        for doc in documentos:
            cuando = 'hoy' if dias == 0 else f'en {dias} días ({doc.fecha_vencimiento:%d/%m/%Y})'
            datos = {'documento_id': str(doc.pk), 'umbral': dias}
            url_empleado = f'/documentos/empleado/{doc.empleado_id}/'

            if doc.empleado.usuario and doc.empleado.usuario.is_active:
                avisos += _avisar(
                    doc.empleado.usuario, tipo, 'Tu documento está por vencer',
                    f'Tu {doc.tipo_documento.nombre.lower()} vence {cuando}. Entrégale el nuevo a Talento Humano.',
                    url_empleado, f'doc-venc-{doc.pk}-{dias}', datos,
                )
            for usuario in rrhh:
                avisos += _avisar(
                    usuario, tipo, 'Documento por vencer',
                    f'{doc.tipo_documento.nombre} de {doc.empleado.nombre_completo} vence {cuando}.',
                    url_empleado, f'doc-venc-{doc.pk}-{dias}-rrhh-{usuario.pk}', datos,
                )
    logger.info(f'Vencimientos de documentos: {avisos} avisos.')
    return avisos
