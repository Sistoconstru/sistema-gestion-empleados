
# =============================================================================
# apps/notifications/models.py
# =============================================================================

import uuid
from django.db import models


class TipoNotificacion(models.Model):
    """Tipos de notificaciones del sistema"""
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    plantilla_titulo = models.CharField(max_length=200)
    plantilla_mensaje = models.TextField()
    plantilla_email = models.TextField(blank=True)
    enviar_email = models.BooleanField(default=False)
    enviar_push = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_notificacion'
        verbose_name = 'Tipo de Notificación'
        verbose_name_plural = 'Tipos de Notificación'
    
    def __str__(self):
        return self.nombre


class Notificacion(models.Model):
    """Notificaciones enviadas a usuarios"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    tipo_notificacion = models.ForeignKey(TipoNotificacion, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    datos_adicionales = models.JSONField(null=True, blank=True)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_leida = models.DateTimeField(null=True, blank=True)
    fecha_envio_email = models.DateTimeField(null=True, blank=True)
    email_enviado = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'notificaciones'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"