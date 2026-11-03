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
    # Si RRHH puede adjuntarle anexos (otrosí, prórrogas...). Hoy: contrato laboral.
    admite_anexos = models.BooleanField(default=False)
    
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
    def save(self, *args, **kwargs):
        import logging
        logger = logging.getLogger('storages')
        backend = type(self.archivo.storage).__name__ if hasattr(self.archivo, 'storage') else 'NoStorage'
        logger.info(f"[DocumentoEmpleado.save] Backend de almacenamiento usado: {backend}")
        super().save(*args, **kwargs)
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
    from custom_storage.media import MediaStorage
    archivo = models.FileField(
        upload_to=get_upload_path,
        storage=MediaStorage()
    )  # Archivo subido
    fecha_documento = models.DateField(null=True, blank=True)  # Fecha del documento
    fecha_vencimiento = models.DateField(null=True, blank=True)  # Fecha de vencimiento
    estado_aprobacion = models.CharField(max_length=20, choices=ESTADOS_APROBACION, default='pendiente')  # Estado de aprobación
    observaciones = models.TextField(blank=True)  # Observaciones opcionales
    fecha_carga = models.DateTimeField(auto_now_add=True)  # Fecha de carga
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)  # Fecha de aprobación
    fecha_rechazo = models.DateTimeField(null=True, blank=True)  # Fecha de rechazo
    cargado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE, related_name='documentos_cargados')  # Usuario que cargó el documento
    aprobado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos_aprobados')  # Usuario que aprobó el documento
    rechazado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos_rechazados')  # Usuario que rechazó el documento
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)  # Fecha de última actualización
    motivo_rechazo = models.TextField(blank=True)  # Motivo del rechazo
    version = models.IntegerField(default=1)  # Número de versión del documento
    
    class Meta:
        db_table = 'documentos_empleado'
        unique_together = ['empleado', 'tipo_documento']  # Un documento por tipo y empleado
        verbose_name = 'Documento de Empleado'
        verbose_name_plural = 'Documentos de Empleado'


def get_upload_path_anexo(instance, filename):
    """documentos/<cedula>/<TIPO>/anexos/<tipo_anexo>_<timestamp>.<ext>"""
    import os
    from django.utils import timezone

    documento = instance.documento
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    _, ext = os.path.splitext(filename)
    return (
        f'documentos/{documento.empleado.numero_documento}/'
        f'{documento.tipo_documento.codigo}/anexos/{instance.tipo}_{timestamp}{ext}'
    )


class VersionDocumento(models.Model):
    """Versión anterior de un DocumentoEmpleado, guardada al reemplazarlo.

    Antes, reemplazar borraba el archivo anterior de S3: un contrato
    actualizado perdía el original. Ahora el archivo se queda donde estaba y
    esta fila conserva sus datos. Solo RRHH ve las versiones anteriores.
    """
    from custom_storage.media import MediaStorage

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    documento = models.ForeignKey(DocumentoEmpleado, on_delete=models.CASCADE, related_name='versiones_anteriores')
    version = models.IntegerField()
    archivo = models.FileField(upload_to=get_upload_path, storage=MediaStorage())
    nombre_archivo = models.CharField(max_length=255)
    fecha_documento = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    estado_aprobacion = models.CharField(max_length=20, choices=DocumentoEmpleado.ESTADOS_APROBACION)
    fecha_carga = models.DateTimeField()
    cargado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, related_name='+')
    aprobado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    # Quién la reemplazó, cuándo y por qué
    reemplazada_en = models.DateTimeField(auto_now_add=True)
    reemplazada_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, related_name='+')
    motivo = models.TextField(blank=True)

    class Meta:
        db_table = 'documentos_empleado_versiones'
        ordering = ['-version']
        verbose_name = 'Versión anterior de documento'
        verbose_name_plural = 'Versiones anteriores de documentos'

    def __str__(self):
        return f'{self.documento} v{self.version}'


class AnexoDocumento(models.Model):
    """Anexo de un documento: otrosí, prórroga, modificación salarial...

    No reemplaza al documento, lo complementa: el contrato sigue vigente y los
    anexos muestran cómo cambió la relación laboral. Los sube RRHH y quedan
    aprobados al cargarlos.
    """
    from custom_storage.media import MediaStorage

    TIPOS = [
        ('otrosi', 'Otrosí'),
        ('prorroga', 'Prórroga'),
        ('modificacion_salarial', 'Modificación salarial'),
        ('cambio_cargo', 'Cambio de cargo'),
        ('cambio_jornada', 'Cambio de jornada'),
        ('otro', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    documento = models.ForeignKey(DocumentoEmpleado, on_delete=models.CASCADE, related_name='anexos')
    tipo = models.CharField(max_length=30, choices=TIPOS)
    fecha_vigencia = models.DateField(help_text='Desde cuándo rige el anexo')
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to=get_upload_path_anexo, storage=MediaStorage())
    nombre_archivo = models.CharField(max_length=255)
    cargado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, related_name='anexos_cargados')
    fecha_carga = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documentos_empleado_anexos'
        ordering = ['fecha_vigencia', 'fecha_carga']
        verbose_name = 'Anexo de documento'
        verbose_name_plural = 'Anexos de documentos'

    def __str__(self):
        return f'{self.get_tipo_display()} {self.fecha_vigencia:%d/%m/%Y} - {self.documento}'
