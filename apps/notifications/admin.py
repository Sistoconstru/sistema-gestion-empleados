from django.contrib import admin

# Register your models here.
# =============================================================================
# apps/notifications/admin.py
# =============================================================================

from django.contrib import admin
from .models import TipoNotificacion, Notificacion, PushSubscription

# Registro del modelo TipoNotificacion en el admin de Django
@admin.register(TipoNotificacion)
class TipoNotificacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'enviar_email', 'enviar_push', 'activo')
    list_filter = ('enviar_email', 'enviar_push', 'activo')

# Registro del modelo Notificacion en el admin de Django
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'titulo', 'leida', 'fecha_creacion', 'email_enviado')
    list_filter = ('leida', 'email_enviado', 'fecha_creacion')
    search_fields = ('usuario__username', 'titulo')


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'user_agent_corto', 'activa', 'fallos_consecutivos', 'fecha_creacion', 'fecha_ultimo_uso')
    list_filter = ('activa', 'fecha_creacion')
    search_fields = ('usuario__username', 'user_agent', 'endpoint')
    readonly_fields = ('endpoint', 'p256dh', 'auth', 'user_agent', 'fecha_creacion', 'fecha_ultimo_uso')
    actions = ['enviar_prueba']

    def user_agent_corto(self, obj):
        return obj.user_agent[:60] if obj.user_agent else '—'
    user_agent_corto.short_description = 'Dispositivo'

    @admin.action(description='Enviar notificación de prueba a las suscripciones seleccionadas')
    def enviar_prueba(self, request, queryset):
        from .push_utils import send_push
        usuarios = {s.usuario for s in queryset}
        for u in usuarios:
            send_push(u, 'SIGHU — prueba desde admin', 'Notificación de prueba enviada desde el admin.', '/dashboard/')
        self.message_user(request, f'Prueba enviada a {len(usuarios)} usuario(s).')
