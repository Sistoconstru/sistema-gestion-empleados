"""Aviso de documentos por vencer y vencidos (campana + push).

Reemplaza al comando check_document_expiry (eliminado), que nunca se
programó: mandaba un correo en cada corrida, sin control de repetidos, y su
reporte a administradores usaba una plantilla que no existía.

Avisa a 30 y 7 días y el día del vencimiento. Lo de después importa tanto
como lo de antes: avisar el día 0 y callarse deja un documento vencido sin
que nadie vuelva a mencionarlo nunca. Así que mientras siga vencido se
sigue recordando, con una cadencia distinta para cada uno, porque son dos
trabajos distintos:

- Al empleado, día por medio hasta que lo actualice. Es quien tiene que ir
  a renovarlo, y un recordatorio seguido es lo que hace que lo haga.
- A Talento Humano, una vez por semana. Revisan una lista, no corren a la
  notaría: doce avisos diarios de lo mismo se vuelven ruido y se dejan de
  leer, que es la forma más segura de que un vencido pase inadvertido.

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
        # No hace falta preguntar si ya lo renovó: `DocumentoEmpleado` es
        # único por (empleado, tipo), así que renovar actualiza esta misma
        # fila y le cambia la fecha. Cuando eso pasa, el documento sale solo
        # de esta consulta y los avisos paran.

        # Dos cadencias distintas porque son dos trabajos distintos. El
        # empleado tiene que ir a renovar, y un recordatorio día por medio
        # es lo que hace que lo haga. Talento Humano revisa la lista, y para
        # eso le basta una vez por semana: doce avisos diarios de lo mismo
        # se vuelven ruido y se dejan de leer.
        tag_empleado, tag_rrhh = _tags(doc, dias, hoy)

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
                url_empleado, tag_empleado, datos,
            )
        for usuario in rrhh:
            avisos += _avisar(
                usuario, tipo, titulo_rrhh, cuerpo_rrhh, url_empleado,
                f'{tag_rrhh}-rrhh-{usuario.pk}', datos,
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


def _tags(doc, dias, hoy):
    """Las etiquetas que marcan "de esto ya se avisó" para cada destinatario.

    La cadencia no se decide con un `if` sobre el día: se decide con la
    etiqueta. El job corre todos los días y la etiqueta solo cambia cuando
    toca avisar de nuevo, así que un día que el servidor esté caído no
    pierde el aviso, solo lo corre al siguiente.

    - Antes del vencimiento: una etiqueta por hito, igual para los dos.
    - Ya vencido: el empleado cambia de etiqueta cada dos días; Talento
      Humano, una vez por semana calendario, así que le llega el lunes —o
      el primer día que el job alcance a correr esa semana.
    """
    if dias >= 0:
        comun = f'doc-venc-{doc.pk}-{dias}'
        return comun, comun

    anio, semana, _ = hoy.isocalendar()
    return (f'doc-venc-{doc.pk}-d{hoy.toordinal() // 2}',
            f'doc-venc-{doc.pk}-s{anio}-{semana:02d}')


