from django.db import models

# =============================================================================
# apps/core/models.py
# =============================================================================

import uuid
from django.db import models
from django.utils import timezone

# Modelo base con campos comunes para heredar en otros modelos
class BaseModel(models.Model):
    """Modelo base con campos comunes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Fecha de última actualización
    activo = models.BooleanField(default=True)  # Estado activo/inactivo
    
    class Meta:
        abstract = True  # No crea tabla, solo sirve para herencia

# Modelo para las configuraciones del sistema
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
    
    modulo = models.CharField(max_length=50)  # Módulo al que pertenece la configuración
    clave = models.CharField(max_length=100)  # Clave de la configuración
    valor = models.TextField()  # Valor actual
    descripcion = models.TextField(blank=True)  # Descripción opcional
    tipo_dato = models.CharField(max_length=20, choices=TIPOS_DATO, default='string')  # Tipo de dato
    valor_defecto = models.TextField(blank=True)  # Valor por defecto
    editable_usuario = models.BooleanField(default=True)  # Si el usuario puede editar
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Fecha de última actualización
    actualizado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)  # Usuario que actualizó
    
    class Meta:
        db_table = 'configuracion_sistema'  # Nombre de la tabla en la BD
        unique_together = ['modulo', 'clave']  # Clave única por módulo y clave
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'

# Modelo para el log de actividades del sistema
class LogActividad(models.Model):
    """Log de actividades del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único
    usuario = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True)  # Usuario que realizó la acción
    accion = models.CharField(max_length=100)  # Acción realizada
    modelo = models.CharField(max_length=50)  # Modelo afectado
    objeto_id = models.UUIDField(null=True, blank=True)  # ID del objeto afectado
    cambios_realizados = models.JSONField(null=True, blank=True)  # Cambios realizados en formato JSON
    ip_address = models.GenericIPAddressField()  # IP desde donde se realizó la acción
    user_agent = models.TextField(blank=True)  # Información del navegador/dispositivo
    metodo_http = models.CharField(max_length=10, blank=True)  # Método HTTP usado
    url_accedida = models.CharField(max_length=500, blank=True)  # URL accedida
    fecha_accion = models.DateTimeField(auto_now_add=True)  # Fecha y hora de la acción
    
    class Meta:
        db_table = 'log_actividades'  # Nombre de la tabla en la BD
        indexes = [
            models.Index(fields=['usuario', 'fecha_accion']),  # Índice para búsquedas por usuario y fecha
            models.Index(fields=['modelo', 'accion']),  # Índice para búsquedas por modelo y acción
        ]
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'
