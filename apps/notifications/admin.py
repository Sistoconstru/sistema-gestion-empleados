from django.contrib import admin

# Register your models here.
# =============================================================================
# apps/notifications/admin.py
# =============================================================================

from django.contrib import admin
from .models import TipoNotificacion, Notificacion

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
