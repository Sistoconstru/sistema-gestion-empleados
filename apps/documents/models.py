from django.db import models

# =============================================================================
# apps/documents/models.py
# =============================================================================

import uuid
from django.db import models

# Función para generar la ruta de subida personalizada para los archivos de documentos
def get_upload_path(instance, filename):
    """Generar ruta de subida personalizada para documentos"""
    import os
    from django.utils import timezone
    
    # Obtener información del empleado y tipo de documento
    empleado_doc = instance.empleado.numero_documento
    tipo_doc = instance.tipo_documento.codigo
    
    # Generar nombre único para evitar conflictos
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{tipo_doc}_{timestamp}{ext}"
    
    # Estructura: documentos/123456789/CEDULA/CEDULA_20240101_120000.pdf
    return f'documentos/{empleado_doc}/{tipo_doc}/{new_filename}'

# Modelo para los tipos de documentos que pueden subir los empleados
class TipoDocumentoEmpleado(models.Model):
    """Tipos de documentos que pueden subir los empleados"""
    codigo = models.CharField(max_length=20, unique=True)  # Código único del tipo de documento
    nombre = models.CharField(max_length=100, unique=True)  # Nombre del tipo de documento
    descripcion = models.TextField(blank=True)  # Descripción opcional
    obligatorio = models.BooleanField(default=False)  # Si el documento es obligatorio
    tiene_vencimiento = models.BooleanField(default=False)  # Si el documento tiene vencimiento
    dias_notificacion_vencimiento = models.IntegerField(default=30)  # Días antes para notificar vencimiento
    formatos_permitidos = models.CharField(max_length=100, default='PDF,JPG,PNG')  # Formatos permitidos
    tamaño_maximo_mb = models.IntegerField(default=5)  # Tamaño máximo en MB
    requiere_aprobacion = models.BooleanField(default=True)  # Si requiere aprobación
    activo = models.BooleanField(default=True)  # Estado activo/inactivo
    
    class Meta:
        db_table = 'tipos_documento_empleado'
        verbose_name = 'Tipo de Documento de Empleado'
        verbose_name_plural = 'Tipos de Documento de Empleado'
    
    def __str__(self):
        return self.nombre

# Modelo para la relación entre tipos de documento y cargos
class TipoDocumentoCargo(models.Model):
    """Relación entre tipos de documento y cargos"""
    tipo_documento = models.ForeignKey(TipoDocumentoEmpleado, on_delete=models.CASCADE)  # Tipo de documento asociado
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)  # Cargo asociado
    
    class Meta:
        db_table = 'tipos_documento_cargos'

# Modelo para los documentos subidos por empleados
class DocumentoEmpleado(models.Model):
    """Documentos subidos por empleados"""
    ESTADOS_APROBACION = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)  # Empleado asociado
    tipo_documento = models.ForeignKey(TipoDocumentoEmpleado, on_delete=models.CASCADE)  # Tipo de documento
    nombre_archivo = models.CharField(max_length=255)  # Nombre del archivo
    archivo = models.FileField(upload_to=get_upload_path)  # Archivo subido
    fecha_documento = models.DateField(null=True, blank=True)  # Fecha del documento
    fecha_vencimiento = models.DateField(null=True, blank=True)  # Fecha de vencimiento
    estado_aprobacion = models.CharField(max_length=20, choices=ESTADOS_APROBACION, default='pendiente')  # Estado de aprobación
    observaciones = models.TextField(blank=True)  # Observaciones opcionales
    fecha_carga = models.DateTimeField(auto_now_add=True)  # Fecha de carga
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)  # Fecha de aprobación
    cargado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE, related_name='documentos_cargados')  # Usuario que cargó el documento
    aprobado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos_aprobados')  # Usuario que aprobó el documento
    
    class Meta:
        db_table = 'documentos_empleado'
        unique_together = ['empleado', 'tipo_documento']  # Un documento por tipo y empleado
        verbose_name = 'Documento de Empleado'
        verbose_name_plural = 'Documentos de Empleado'
