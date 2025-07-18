from django.db import models

# Create your models here.
# =============================================================================
# apps/core/models.py
# =============================================================================

import uuid
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Modelo base con campos comunes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        abstract = True


class ConfiguracionSistema(models.Model):
    """Configuraciones del sistema"""
    TIPOS_DATO = [
        ('string', 'Texto'),
        ('integer', 'Entero'),
        ('decimal', 'Decimal'),
        ('boolean', 'Booleano'),
        ('date', 'Fecha'),
        ('datetime', 'Fecha y Hora'),
        ('json', 'JSON'),
    ]
    
    modulo = models.CharField(max_length=50)
    clave = models.CharField(max_length=100)
    valor = models.TextField()
    descripcion = models.TextField(blank=True)
    tipo_dato = models.CharField(max_length=20, choices=TIPOS_DATO, default='string')
    valor_defecto = models.TextField(blank=True)
    editable_usuario = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'configuracion_sistema'
        unique_together = ['modulo', 'clave']
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'


class LogActividad(models.Model):
    """Log de actividades del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=100)
    modelo = models.CharField(max_length=50)
    objeto_id = models.UUIDField(null=True, blank=True)
    cambios_realizados = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    metodo_http = models.CharField(max_length=10, blank=True)
    url_accedida = models.CharField(max_length=500, blank=True)
    fecha_accion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'log_actividades'
        indexes = [
            models.Index(fields=['usuario', 'fecha_accion']),
            models.Index(fields=['modelo', 'accion']),
        ]
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'
