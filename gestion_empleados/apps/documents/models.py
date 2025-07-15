from django.db import models

# Create your models here.
# =============================================================================
# apps/documents/models.py
# =============================================================================

import uuid
from django.db import models


class TipoDocumentoEmpleado(models.Model):
    """Tipos de documentos que pueden subir los empleados"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    obligatorio = models.BooleanField(default=False)
    tiene_vencimiento = models.BooleanField(default=False)
    dias_notificacion_vencimiento = models.IntegerField(default=30)
    formatos_permitidos = models.CharField(max_length=100, default='PDF,JPG,PNG')
    tamaño_maximo_mb = models.IntegerField(default=5)
    requiere_aprobacion = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_documento_empleado'
        verbose_name = 'Tipo de Documento de Empleado'
        verbose_name_plural = 'Tipos de Documento de Empleado'
    
    def __str__(self):
        return self.nombre


class TipoDocumentoCargo(models.Model):
    """Relación entre tipos de documento y cargos"""
    tipo_documento = models.ForeignKey(TipoDocumentoEmpleado, on_delete=models.CASCADE)
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'tipos_documento_cargos'


class DocumentoEmpleado(models.Model):
    """Documentos subidos por empleados"""
    ESTADOS_APROBACION = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)
    tipo_documento = models.ForeignKey(TipoDocumentoEmpleado, on_delete=models.CASCADE)
    nombre_archivo = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='documentos/')
    fecha_documento = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    estado_aprobacion = models.CharField(max_length=20, choices=ESTADOS_APROBACION, default='pendiente')
    observaciones = models.TextField(blank=True)
    fecha_carga = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    cargado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE, related_name='documentos_cargados')
    aprobado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos_aprobados')
    
    class Meta:
        db_table = 'documentos_empleado'
        unique_together = ['empleado', 'tipo_documento']
        verbose_name = 'Documento de Empleado'
        verbose_name_plural = 'Documentos de Empleado'
