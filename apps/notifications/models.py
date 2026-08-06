# =============================================================================
# apps/notifications/models.py
# =============================================================================

import uuid
from django.db import models


class TipoNotificacion(models.Model):
    """Tipos de notificaciones del sistema"""
    codigo = models.CharField(max_length=30, unique=True)  # Código único para el tipo de notificación
    nombre = models.CharField(max_length=100, unique=True)  # Nombre del tipo de notificación
    descripcion = models.TextField(blank=True)  # Descripción opcional
    plantilla_titulo = models.CharField(max_length=200)  # Plantilla para el título de la notificación
    plantilla_mensaje = models.TextField()  # Plantilla para el mensaje de la notificación
    plantilla_email = models.TextField(blank=True)  # Plantilla para el email (opcional)
    enviar_email = models.BooleanField(default=False)  # Si se debe enviar por email
    enviar_push = models.BooleanField(default=True)  # Si se debe enviar como push
    activo = models.BooleanField(default=True)  # Estado activo/inactivo
    
    class Meta:
        db_table = 'tipos_notificacion'
        verbose_name = 'Tipo de Notificación'
        verbose_name_plural = 'Tipos de Notificación'
    
    def __str__(self):
        return self.nombre


class Notificacion(models.Model):
    """Notificaciones enviadas a usuarios"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único
    usuario = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)  # Usuario destinatario
    tipo_notificacion = models.ForeignKey(TipoNotificacion, on_delete=models.CASCADE)  # Tipo de notificación
    titulo = models.CharField(max_length=200)  # Título de la notificación
    mensaje = models.TextField()  # Mensaje de la notificación
    datos_adicionales = models.JSONField(null=True, blank=True)  # Datos extra en formato JSON
    leida = models.BooleanField(default=False)  # Si la notificación fue leída
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    fecha_leida = models.DateTimeField(null=True, blank=True)  # Fecha en que fue leída
    fecha_envio_email = models.DateTimeField(null=True, blank=True)  # Fecha de envío de email
    email_enviado = models.BooleanField(default=False)  # Si se envió el email
    
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

class PushSubscription(models.Model):
    """Suscripción de Web Push por dispositivo/navegador.

    Un usuario puede tener varias (celular + laptop, etc.). El endpoint
    identifica de forma única la suscripción emitida por el navegador;
    p256dh y auth son las claves que devuelve pushManager.subscribe() y
    que pywebpush necesita para cifrar el payload.
    """
    usuario = models.ForeignKey(
        'authentication.Usuario', on_delete=models.CASCADE,
        related_name='push_subscriptions',
    )
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=200)
    user_agent = models.CharField(max_length=300, blank=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_uso = models.DateTimeField(null=True, blank=True)
    fallos_consecutivos = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'push_subscriptions'
        verbose_name = 'Suscripción push'
        verbose_name_plural = 'Suscripciones push'
        indexes = [
            models.Index(fields=['usuario', 'activa']),
        ]

    def __str__(self):
        return f"{self.usuario.username} — {self.user_agent[:40] or 'device'}"
