from django.db import models

# Create your models here.

# =============================================================================
# apps/reports/models.py
# =============================================================================

import uuid
from django.db import models


class TipoReporte(models.Model):
    """Tipos de reportes del sistema"""
    FORMATOS = [
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=50)
    consulta_sql = models.TextField(blank=True)
    parametros_requeridos = models.JSONField(null=True, blank=True)
    formato_salida = models.CharField(max_length=20, choices=FORMATOS, default='excel')
    programable = models.BooleanField(default=False)
    tiempo_cache_minutos = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'tipos_reporte'
        verbose_name = 'Tipo de Reporte'
        verbose_name_plural = 'Tipos de Reporte'
    
    def __str__(self):
        return self.nombre


class TipoReporteRol(models.Model):
    """Relación entre tipos de reporte y roles"""
    tipo_reporte = models.ForeignKey(TipoReporte, on_delete=models.CASCADE)
    rol = models.ForeignKey('authentication.Rol', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'tipos_reporte_roles'


class ReporteGenerado(models.Model):
    """Reportes generados por usuarios"""
    ESTADOS = [
        ('generando', 'Generando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
        ('expirado', 'Expirado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_reporte = models.ForeignKey(TipoReporte, on_delete=models.CASCADE)
    usuario = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    nombre_archivo = models.CharField(max_length=255)
    parametros_utilizados = models.JSONField(null=True, blank=True)
    archivo_generado = models.FileField(upload_to='reportes/', blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    tiempo_generacion_segundos = models.IntegerField(null=True, blank=True)
    tamaño_archivo_bytes = models.BigIntegerField(null=True, blank=True)
    numero_registros = models.IntegerField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='generando')
    mensaje_error = models.TextField(blank=True)
    
    class Meta:
        db_table = 'reportes_generados'
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'