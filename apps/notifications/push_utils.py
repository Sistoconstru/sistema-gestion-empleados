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


def send_push(usuario, title, body, url='/', icon='/static/pwa/icon-192.png', tag=None):
    """Envía una notificación push a todas las suscripciones activas del usuario.

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
    payload = json.dumps({
        'title': title,
        'body': body,
        'url': url,
        'icon': icon,
        'tag': tag or f'sighu-{timezone.now().timestamp()}',
    })

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
