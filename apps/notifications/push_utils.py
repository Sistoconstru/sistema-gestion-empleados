"""Utilidades de Web Push.

Encapsula el envío usando pywebpush y VAPID. Silencia suscripciones que ya
no son válidas (404/410) marcándolas como inactivas para no reintentar en
el próximo ciclo.
"""
import json
import logging

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def _vapid_claims():
    return {"sub": settings.VAPID_ADMIN_EMAIL}


def send_push(usuario, title, body, url='/', icon=None,
              tag=None, tag_group=None, actions=None, action_urls=None,
              vibrate=None):
    """Envía una notificación push a todas las suscripciones activas del usuario.

    Parámetros:
        tag       — id único de la notificación (para reemplazar duplicados exactos).
        tag_group — id de agrupación por tipo (ej: 'novedad', 'sesion'); si
                    varias notif del mismo grupo llegan, el navegador reemplaza
                    en vez de acumular en la barra. Sobrepone a `tag`.
        actions   — lista de {action, title, icon?}; Android desktop las
                    muestra como botones. Máx 2 en Chrome.
        action_urls — dict {action: url}; se usa al hacer clic en el botón.
        vibrate   — patrón de vibración Android, ej [200, 100, 200].

    Devuelve (enviadas, desactivadas). Nunca lanza excepción — cualquier fallo
    queda en el log y en `fallos_consecutivos` de la suscripción; tras 3 fallos
    marca la suscripción como inactiva.
    """
    from pywebpush import webpush, WebPushException
    from .models import PushSubscription

    if not (settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY):
        logger.warning('VAPID keys no configuradas; no se envía push.')
        return 0, 0

    subs = PushSubscription.objects.filter(usuario=usuario, activa=True)
    if icon is None:
        # Se resuelve aquí (no en el default arg) para que respete el manifest
        # de whitenoise en producción (nombre hasheado).
        from django.templatetags.static import static
        icon = static('pwa/icon-192.png')
    payload_dict = {
        'title': title,
        'body': body,
        'url': url,
        'icon': icon,
        'tag': tag or f'sighu-{timezone.now().timestamp()}',
    }
    if tag_group:
        payload_dict['tagGroup'] = tag_group
    if actions:
        payload_dict['actions'] = actions
    if action_urls:
        payload_dict['actionUrls'] = action_urls
    if vibrate is not None:
        payload_dict['vibrate'] = vibrate
    payload = json.dumps(payload_dict)

    enviadas = 0
    desactivadas = 0
    for sub in subs:
        try:
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims=_vapid_claims(),
                ttl=60 * 60 * 24,  # 24h — si el disp está offline, guarda y entrega al conectarse
            )
            sub.fallos_consecutivos = 0
            sub.fecha_ultimo_uso = timezone.now()
            sub.save(update_fields=['fallos_consecutivos', 'fecha_ultimo_uso'])
            enviadas += 1
        except WebPushException as e:
            # 404/410 = suscripción cancelada por el navegador (usuario limpió datos,
            # desinstaló, etc.) — desactivar de una.
            status = getattr(e.response, 'status_code', None) if e.response else None
            if status in (404, 410):
                sub.activa = False
                sub.save(update_fields=['activa'])
                desactivadas += 1
                logger.info(f'Push subscription {sub.pk} desactivada (status {status}).')
            else:
                sub.fallos_consecutivos += 1
                if sub.fallos_consecutivos >= 3:
                    sub.activa = False
                    desactivadas += 1
                sub.save(update_fields=['fallos_consecutivos', 'activa'])
                logger.warning(f'Fallo push subscription {sub.pk}: {e}')
        except Exception as e:
            logger.error(f'Excepción inesperada enviando push a {usuario.username}: {e}')

    return enviadas, desactivadas
