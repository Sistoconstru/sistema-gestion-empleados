"""Vistas relacionadas a la PWA y suscripciones Web Push."""
import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import TemplateView

from .models import PushSubscription

logger = logging.getLogger(__name__)


@require_GET
@cache_control(max_age=3600, public=True)
def manifest(request):
    """Manifest de la PWA — sirve el JSON con nombre, colores e íconos."""
    data = {
        "name": "SIGHU C.I.",
        "short_name": "SIGHU",
        "description": "Sistema de Gestión de Empleados — Construinmuniza",
        "start_url": "/dashboard/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait-primary",
        "background_color": "#ffffff",
        "theme_color": "#0e5f3f",
        "lang": "es-CO",
        "icons": [
            {
                "src": "/static/pwa/icon-192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": "/static/pwa/icon-512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
        "shortcuts": [
            {
                "name": "Mis capacitaciones",
                "url": "/capacitaciones/mis-capacitaciones/",
                "icons": [{"src": "/static/pwa/icon-192.png", "sizes": "192x192"}],
            },
            {
                "name": "Sesiones a mi cargo",
                "url": "/capacitaciones/sesiones/a-cargo/",
                "icons": [{"src": "/static/pwa/icon-192.png", "sizes": "192x192"}],
            },
        ],
    }
    return JsonResponse(data)


@require_GET
def service_worker(request):
    """Sirve el service worker desde la raíz (necesario para scope global)."""
    from django.template.loader import render_to_string
    body = render_to_string('notifications/pwa/service_worker.js', {})
    resp = HttpResponse(body, content_type='application/javascript')
    resp['Service-Worker-Allowed'] = '/'
    # Ojo: el SW no debe cachearse por defecto — que el navegador siempre
    # revalide para captar cambios rápidos durante desarrollo.
    resp['Cache-Control'] = 'no-cache'
    return resp


@require_GET
def vapid_public_key(request):
    """Devuelve la public key VAPID que el JS necesita para pushManager.subscribe()."""
    return JsonResponse({'public_key': settings.VAPID_PUBLIC_KEY})


@login_required
@ensure_csrf_cookie
@require_POST
def subscribe(request):
    """Guarda o actualiza la suscripción push del usuario para este dispositivo."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        endpoint = data['endpoint']
        keys = data['keys']
        p256dh = keys['p256dh']
        auth = keys['auth']
    except (KeyError, ValueError, TypeError) as e:
        return JsonResponse({'ok': False, 'error': f'payload inválido: {e}'}, status=400)

    ua = request.META.get('HTTP_USER_AGENT', '')[:300]
    sub, created = PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            'usuario': request.user,
            'p256dh': p256dh,
            'auth': auth,
            'user_agent': ua,
            'activa': True,
            'fallos_consecutivos': 0,
        },
    )
    logger.info(f'PushSubscription {"creada" if created else "actualizada"} para {request.user.username}')
    return JsonResponse({'ok': True, 'created': created})


@login_required
@require_POST
def unsubscribe(request):
    """Marca la suscripción de este dispositivo como inactiva."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        endpoint = data['endpoint']
    except (KeyError, ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'payload inválido'}, status=400)

    PushSubscription.objects.filter(endpoint=endpoint, usuario=request.user).update(activa=False)
    return JsonResponse({'ok': True})


@login_required
@require_POST
def send_test(request):
    """Envía una notificación de prueba al usuario logueado — para debug."""
    from .push_utils import send_push
    enviadas, desactivadas = send_push(
        request.user,
        title='SIGHU — prueba',
        body='Si ves esto, las notificaciones están funcionando 🎉',
        url='/dashboard/',
    )
    return JsonResponse({'ok': True, 'enviadas': enviadas, 'desactivadas': desactivadas})


class OfflinePage(TemplateView):
    template_name = 'notifications/pwa/offline.html'


from django.contrib.auth.mixins import LoginRequiredMixin


class NotificacionesSettingsView(LoginRequiredMixin, TemplateView):
    """Página para que el empleado active/desactive notificaciones push
    y pueda probar el envío."""
    template_name = 'notifications/pwa/settings.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['subs_activas'] = PushSubscription.objects.filter(
            usuario=self.request.user, activa=True,
        ).order_by('-fecha_creacion')
        return ctx
