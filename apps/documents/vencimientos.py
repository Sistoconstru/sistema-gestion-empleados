"""Aviso de documentos por vencer y vencidos (campana + push).

Reemplaza al comando check_document_expiry (eliminado), que nunca se
programó: mandaba un correo en cada corrida, sin control de repetidos, y su
reporte a administradores usaba una plantilla que no existía.

Avisa a 30 y 7 días, el día del vencimiento, y después una vez por semana
mientras siga vencido. Lo de después del vencimiento importa tanto como lo
de antes: avisar el día 0 y callarse deja un documento vencido sin que
nadie vuelva a mencionarlo nunca.

Se incluyen los documentos pendientes de aprobación, no solo los aprobados.
Uno pendiente también se vence, y dejarlo fuera significaba que el empleado
que subió su licencia y nadie revisó no recibía ningún aviso. Los
rechazados sí quedan fuera: ese documento no vale de todas formas.

Idempotente por (documento, umbral) vía push_tag: correr el job dos veces
el mismo día, o un día con el servidor caído y reiniciado, no repite
avisos. Para lo ya vencido el umbral es la semana corrida desde que venció,
así que un documento que llevaba meses vencido cuando se instaló esto se
avisa en la primera corrida, sin esperar a que cuadre el múltiplo de siete.
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

    # Una sola pasada sobre lo que está vencido o a punto, en vez de una
    # consulta por umbral: así lo ya vencido entra sin inventar más rondas.
    documentos = (DocumentoEmpleado.objects
                  .filter(fecha_vencimiento__isnull=False,
                          fecha_vencimiento__lte=hoy + timedelta(days=max(UMBRALES_DIAS)))
                  .exclude(estado_aprobacion='rechazado')
                  .select_related('empleado__usuario', 'tipo_documento'))

    avisos = 0
    for doc in documentos:
        dias = (doc.fecha_vencimiento - hoy).days
        umbral = _umbral(dias)
        if umbral is None:
            continue

        url_empleado = f'/documentos/empleado/{doc.empleado_id}/'
        datos = {'documento_id': str(doc.pk), 'umbral': umbral,
                 'vencido': dias < 0}
        nombre = doc.tipo_documento.nombre
        sin_aprobar = doc.estado_aprobacion != 'aprobado'

        if dias < 0:
            titulo_empleado = 'Tienes un documento vencido'
            cuerpo_empleado = (
                f'Tu {nombre.lower()} venció hace {abs(dias)} días '
                f'({doc.fecha_vencimiento:%d/%m/%Y}). Entrégale el nuevo a '
                f'Talento Humano.')
            titulo_rrhh = 'Documento vencido'
            cuerpo_rrhh = (
                f'{nombre} de {doc.empleado.nombre_completo} venció hace '
                f'{abs(dias)} días ({doc.fecha_vencimiento:%d/%m/%Y}).')
        else:
            cuando = 'hoy' if dias == 0 else f'en {dias} días ({doc.fecha_vencimiento:%d/%m/%Y})'
            titulo_empleado = 'Tu documento está por vencer'
            cuerpo_empleado = (f'Tu {nombre.lower()} vence {cuando}. '
                               f'Entrégale el nuevo a Talento Humano.')
            titulo_rrhh = 'Documento por vencer'
            cuerpo_rrhh = (f'{nombre} de {doc.empleado.nombre_completo} '
                           f'vence {cuando}.')

        if sin_aprobar:
            # A Talento Humano le cambia la tarea: además de pedir el nuevo,
            # tiene uno sin revisar encima de la mesa.
            cuerpo_rrhh += ' El documento sigue pendiente de aprobación.'

        if doc.empleado.usuario and doc.empleado.usuario.is_active:
            avisos += _avisar(
                doc.empleado.usuario, tipo, titulo_empleado, cuerpo_empleado,
                url_empleado, f'doc-venc-{doc.pk}-{umbral}', datos,
            )
        for usuario in rrhh:
            avisos += _avisar(
                usuario, tipo, titulo_rrhh, cuerpo_rrhh, url_empleado,
                f'doc-venc-{doc.pk}-{umbral}-rrhh-{usuario.pk}', datos,
            )

    logger.info(f'Vencimientos de documentos: {avisos} avisos.')
    return avisos


def _umbral(dias):
    """A qué aviso corresponde este documento hoy, o None si a ninguno.

    Antes del vencimiento son hitos exactos. Después, la semana corrida:
    `-1` la primera semana vencido, `-2` la segunda. Contarlo por semanas
    cumplidas y no por "días divisibles entre siete" es lo que hace que un
    documento vencido hace meses se avise en la primera corrida en vez de
    esperar a que el número cuadre.
    """
    if dias >= 0:
        return dias if dias in UMBRALES_DIAS else None
    return -((abs(dias) // 7) + 1)
