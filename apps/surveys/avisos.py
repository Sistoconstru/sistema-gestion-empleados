"""Avisos de encuestas: publicación, recordatorios y aviso a jefes.

Un solo lugar para decidir a quién se avisa y para no avisar dos veces. Lo usan
la señal de publicación, el job diario del scheduler y el botón "Avisar a
pendientes" de RRHH.

Idempotencia por `push_tag` en Notificacion.datos_adicionales:
- publicación:  encuesta-pub-{encuesta}-{usuario}           (una vez en la vida)
- recordatorio: encuesta-rec-{encuesta}-{usuario}-{fecha}    (una vez por día)
- jefe:         encuesta-jefe-{encuesta}-{usuario}-{fecha}   (una vez por día)
El recordatorio manual y los automáticos comparten tag: nadie recibe dos
recordatorios el mismo día.
"""
import logging
import threading
from collections import defaultdict
from datetime import date, timedelta

from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)

TIPOS = {
    'encuesta_publicada': ('Encuesta publicada', 'Aviso al empleado cuando se publica una encuesta.'),
    'encuesta_recordatorio': ('Recordatorio de encuesta', 'Recordatorio a quien no ha respondido.'),
    'encuesta_jefe': ('Encuesta pendiente en el equipo', 'Aviso al jefe con los pendientes de su equipo.'),
}


def _fecha(valor):
    """Las vistas pueden dejar la fecha como texto en la instancia ("2026-11-06")
    y formatear un str con %d/%m/%Y lanza ValueError: eso tumbó el aviso de
    publicación de la encuesta de la fiesta. Se normaliza aquí."""
    return valor if isinstance(valor, date) else date.fromisoformat(str(valor))


def en_segundo_plano(funcion, *args):
    """Corre el envío fuera de la petición web.

    Mandar push a cientos de personas toma más que los 30 s que gunicorn da a
    una petición; si se cortara a mitad, la mitad se quedaría sin aviso. Las
    etiquetas idempotentes hacen seguro repetir un envío interrumpido.
    """
    def _correr():
        try:
            funcion(*args)
        except Exception:
            logger.exception(f'Fallo enviando avisos de encuesta ({funcion.__name__})')
        finally:
            close_old_connections()

    threading.Thread(target=_correr, daemon=True).start()


def esta_vigente(encuesta, hoy=None):
    """Publicada, abierta hoy y con preguntas: lo mínimo para avisar."""
    hoy = hoy or timezone.localdate()
    return (
        encuesta.activa
        and not encuesta.es_borrador
        and _fecha(encuesta.fecha_inicio) <= hoy <= _fecha(encuesta.fecha_fin)
        and encuesta.preguntaencuesta_set.filter(activa=True).exists()
    )


def destinatarios_pendientes(encuesta):
    """Empleados que deben responder y no han terminado.

    Unión de los destinatarios por cargo/área (o toda la empresa) y de quienes
    tienen participación asignada, menos los que ya la completaron.
    """
    from apps.employees.models import Empleado
    from .models import ParticipacionEncuesta
    from .views import _destinatarios_encuesta

    destinatarios = set(_destinatarios_encuesta(encuesta).values_list('pk', flat=True))
    asignados = set(
        ParticipacionEncuesta.objects.filter(encuesta=encuesta, empleado__isnull=False)
        .values_list('empleado_id', flat=True)
    )
    completados = set(
        ParticipacionEncuesta.objects.filter(encuesta=encuesta, completada=True, empleado__isnull=False)
        .values_list('empleado_id', flat=True)
    )
    return (
        Empleado.objects.filter(pk__in=(destinatarios | asignados) - completados)
        .filter(usuario__isnull=False, usuario__is_active=True)
        .select_related('usuario')
    )


def encuestas_pendientes_de(empleado, hoy=None):
    """Encuestas abiertas que este empleado debe responder y no ha terminado.

    Misma regla que destinatarios_pendientes, vista desde el empleado. No
    depende de que ya exista su participación: en una encuesta general esta
    solo se crea al abrirla, y el contador del menú no veía a quien nunca la
    había abierto.
    """
    from .models import Encuesta, ParticipacionEncuesta
    from .views import _destinatarios_encuesta

    hoy = hoy or timezone.localdate()
    participaciones = dict(
        ParticipacionEncuesta.objects.filter(empleado=empleado).values_list('encuesta_id', 'completada')
    )
    pendientes = []
    for encuesta in Encuesta.objects.filter(
        activa=True, fecha_publicacion__isnull=False,
        fecha_inicio__lte=hoy, fecha_fin__gte=hoy,
    ).order_by('fecha_fin'):
        if participaciones.get(encuesta.pk):
            continue  # completada
        if encuesta.pk in participaciones or _destinatarios_encuesta(encuesta).filter(pk=empleado.pk).exists():
            pendientes.append(encuesta)
    return pendientes


def _tipo(codigo):
    from apps.notifications.models import TipoNotificacion
    nombre, descripcion = TIPOS[codigo]
    tipo, _ = TipoNotificacion.objects.get_or_create(
        codigo=codigo,
        defaults={
            'nombre': nombre, 'descripcion': descripcion,
            'plantilla_titulo': nombre, 'plantilla_mensaje': descripcion,
            'enviar_email': False, 'enviar_push': True, 'activo': True,
        },
    )
    return tipo


def _ya_enviado(usuario, tag):
    from apps.notifications.models import Notificacion
    return Notificacion.objects.filter(
        usuario=usuario, datos_adicionales__contains={'push_tag': tag},
    ).exists()


def _enviar(usuario, tipo, titulo, cuerpo, url, tag, datos):
    """Campana siempre; push si el usuario tiene dispositivo. Devuelve True si
    llegó por push."""
    from apps.notifications.models import Notificacion
    from apps.notifications.push_utils import send_push

    # La campana va primero: si el push falla, el aviso igual queda en el sistema.
    Notificacion.objects.create(
        usuario=usuario, tipo_notificacion=tipo, titulo=titulo, mensaje=cuerpo,
        datos_adicionales={'push_tag': tag, **datos},
    )
    enviadas, _ = send_push(
        usuario, titulo, cuerpo, url=url, tag=tag, tag_group='encuesta',
        actions=[{'action': 'abrir', 'title': 'Abrir'}], action_urls={'abrir': url},
    )
    return enviadas > 0


def avisar_publicacion(encuesta_pk):
    """"Nueva encuesta disponible" a los pendientes que aún no lo recibieron.

    Si la encuesta todavía no abre (fecha_inicio futura), no hace nada: el job
    diario la avisa el día de inicio.
    """
    from .models import Encuesta
    encuesta = Encuesta.objects.get(pk=encuesta_pk)
    if not esta_vigente(encuesta):
        return {'enviados': 0, 'push': 0}

    tipo = _tipo('encuesta_publicada')
    fin = _fecha(encuesta.fecha_fin)
    titulo = 'Nueva encuesta disponible'
    cuerpo = f'{encuesta.nombre}. Cierra el {fin:%d/%m/%Y}. Toca para responderla.'
    url = f'/encuestas/responder/{encuesta.pk}/'

    from apps.notifications.models import Notificacion
    # Quien ya recibió cualquier aviso de esta encuesta (p. ej. un recordatorio
    # manual antes de que corriera el job) no necesita el de "nueva encuesta".
    ya_avisados = set(
        Notificacion.objects.filter(datos_adicionales__contains={'encuesta_id': str(encuesta.pk)})
        .values_list('usuario_id', flat=True)
    )

    enviados = push = 0
    for emp in destinatarios_pendientes(encuesta):
        tag = f'encuesta-pub-{encuesta.pk}-{emp.usuario.pk}'
        if emp.usuario_id in ya_avisados or _ya_enviado(emp.usuario, tag):
            continue
        try:
            push += _enviar(emp.usuario, tipo, titulo, cuerpo, url, tag,
                            {'encuesta_id': str(encuesta.pk)})
            enviados += 1
        except Exception as e:
            logger.warning(f'Fallo avisando encuesta {encuesta.codigo} a {emp.usuario.username}: {e}')

    logger.info(f'Encuesta {encuesta.codigo} publicada: {enviados} avisos, {push} por push.')
    return {'enviados': enviados, 'push': push}


def recordar_pendientes(encuesta_pk, motivo):
    """Recordatorio a cada pendiente y aviso a sus jefes.

    motivo: 'cierre' (cierra mañana), 'mitad' (mitad del plazo) o 'manual'
    (botón de RRHH). Solo cambia el texto.
    """
    from .models import Encuesta
    encuesta = Encuesta.objects.get(pk=encuesta_pk)
    if not esta_vigente(encuesta):
        return {'enviados': 0, 'push': 0, 'jefes': 0}

    hoy = timezone.localdate()
    tipo = _tipo('encuesta_recordatorio')
    fin = _fecha(encuesta.fecha_fin)
    if motivo == 'cierre':
        titulo = 'Encuesta cierra mañana'
        cuerpo = f'"{encuesta.nombre}" cierra el {fin:%d/%m/%Y}. Aún no la has respondido.'
    else:
        titulo = 'Tienes una encuesta pendiente'
        cuerpo = f'"{encuesta.nombre}" cierra el {fin:%d/%m/%Y}. Te toma pocos minutos.'
    url = f'/encuestas/responder/{encuesta.pk}/'

    pendientes = list(destinatarios_pendientes(encuesta))
    enviados = push = 0
    for emp in pendientes:
        tag = f'encuesta-rec-{encuesta.pk}-{emp.usuario.pk}-{hoy.isoformat()}'
        if _ya_enviado(emp.usuario, tag):
            continue
        try:
            push += _enviar(emp.usuario, tipo, titulo, cuerpo, url, tag,
                            {'encuesta_id': str(encuesta.pk), 'fecha': hoy.isoformat(), 'motivo': motivo})
            enviados += 1
        except Exception as e:
            logger.warning(f'Fallo recordando encuesta {encuesta.codigo} a {emp.usuario.username}: {e}')

    jefes = avisar_jefes(encuesta, pendientes, hoy)
    logger.info(
        f'Encuesta {encuesta.codigo} recordatorio ({motivo}): {enviados} avisos, '
        f'{push} por push, {jefes} jefes.'
    )
    return {'enviados': enviados, 'push': push, 'jefes': jefes}


def pendientes_por_jefe(pendientes):
    """{jefe: [subalternos pendientes]} según HistorialCargo.jefe_directo activo."""
    from apps.employees.models import Empleado, HistorialCargo
    ids = [e.pk for e in pendientes]
    jefe_de = dict(
        HistorialCargo.objects.filter(empleado_id__in=ids, activo=True, jefe_directo__isnull=False)
        .values_list('empleado_id', 'jefe_directo_id')
    )
    agrupados = defaultdict(list)
    for emp in pendientes:
        if emp.pk in jefe_de:
            agrupados[jefe_de[emp.pk]].append(emp)
    jefes = Empleado.objects.filter(
        pk__in=agrupados.keys(), usuario__isnull=False, usuario__is_active=True,
    ).select_related('usuario')
    return {jefe: agrupados[jefe.pk] for jefe in jefes}


def avisar_jefes(encuesta, pendientes, hoy):
    """Cada jefe con gente pendiente recibe cuántos son y un enlace a la lista.

    Es la vía para llegar a quien no entra al sistema: el jefe se lo recuerda
    en persona.
    """
    tipo = _tipo('encuesta_jefe')
    fin = _fecha(encuesta.fecha_fin)
    url = f'/encuestas/equipo/{encuesta.pk}/'
    avisados = 0
    for jefe, equipo in pendientes_por_jefe(pendientes).items():
        tag = f'encuesta-jefe-{encuesta.pk}-{jefe.usuario.pk}-{hoy.isoformat()}'
        if _ya_enviado(jefe.usuario, tag):
            continue
        n = len(equipo)
        cuerpo = (
            f'{n} persona{"s" if n != 1 else ""} de tu equipo no ha{"n" if n != 1 else ""} '
            f'respondido "{encuesta.nombre}" (cierra el {fin:%d/%m/%Y}). Toca para ver quiénes.'
        )
        try:
            _enviar(jefe.usuario, tipo, 'Encuesta pendiente en tu equipo', cuerpo, url, tag,
                    {'encuesta_id': str(encuesta.pk), 'fecha': hoy.isoformat(), 'pendientes': n})
            avisados += 1
        except Exception as e:
            logger.warning(f'Fallo avisando a jefe {jefe.usuario.username}: {e}')
    return avisados


def mantenimiento_diario(hoy=None):
    """Job de las 7:00: publica lo que abre hoy y manda los recordatorios.

    - Publicación: encuestas vigentes cuyo aviso aún no le llegó a alguien
      (abrieron hoy, o se publicaron antes de su fecha de inicio).
    - Mitad del plazo: si la encuesta dura 4 días o más.
    - Víspera del cierre.
    """
    from .models import Encuesta
    hoy = hoy or timezone.localdate()
    for encuesta in Encuesta.objects.filter(
        activa=True, fecha_publicacion__isnull=False,
        fecha_inicio__lte=hoy, fecha_fin__gte=hoy,
    ):
        avisar_publicacion(encuesta.pk)
        duracion = (encuesta.fecha_fin - encuesta.fecha_inicio).days
        mitad = encuesta.fecha_inicio + timedelta(days=duracion // 2)
        if (encuesta.fecha_fin - hoy).days == 1:
            recordar_pendientes(encuesta.pk, 'cierre')
        elif duracion >= 4 and hoy == mitad:
            recordar_pendientes(encuesta.pk, 'mitad')
