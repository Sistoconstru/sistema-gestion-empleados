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
    descripcion = models.TextField(blank=True)  # Descripción legible de la acción
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

    def __str__(self):
        return self.descripcion or f"{self.usuario} - {self.accion} - {self.modelo}"


def _documento_corporativo_upload_path(instance, filename):
    """Ruta de almacenamiento: documentos_corporativos/<categoria>/<filename_safe>."""
    import os
    from django.utils.text import slugify
    base, ext = os.path.splitext(filename or '')
    ext = (ext or '').lower()[:10]
    base_safe = slugify(base)[:80] or 'documento'
    return f"documentos_corporativos/{instance.categoria}/{base_safe}{ext}"


class DocumentoCorporativo(models.Model):
    """Documentos institucionales disponibles para consulta de los empleados.

    Reglamentos, políticas, manuales, procedimientos, etc. Se publican desde
    el admin de Django y aparecen agrupados por categoría en la sección
    'Documentos institucionales' del perfil del empleado.
    """
    from custom_storage.media import MediaStorage

    CATEGORIAS = [
        ('reglamento', 'Reglamentos'),
        ('politica', 'Políticas'),
        ('manual', 'Manuales'),
        ('procedimiento', 'Procedimientos'),
        ('formato', 'Formatos'),
        ('otro', 'Otros'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, help_text='Resumen breve del contenido del documento')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='reglamento')
    archivo = models.FileField(
        upload_to=_documento_corporativo_upload_path,
        max_length=500,
        storage=MediaStorage(),
        help_text='PDF, DOCX o imagen',
    )
    version = models.CharField(max_length=20, blank=True, help_text='Ej: v1.0, 2026, etc.')
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    fecha_vigencia_desde = models.DateField(null=True, blank=True)
    fecha_vigencia_hasta = models.DateField(null=True, blank=True, help_text='Opcional, si el documento tiene vencimiento')
    activo = models.BooleanField(default=True, help_text='Si está activo, aparece en la sección de documentos del empleado')
    creado_por = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='documentos_corporativos_creados',
    )

    class Meta:
        db_table = 'documentos_corporativos'
        ordering = ['categoria', '-fecha_publicacion']
        verbose_name = 'Documento Corporativo'
        verbose_name_plural = 'Documentos Corporativos'
        indexes = [
            models.Index(fields=['activo', 'categoria']),
        ]

    def __str__(self):
        return f"{self.get_categoria_display()}: {self.titulo}"

    @property
    def filename(self):
        if not self.archivo:
            return ''
        import os
        return os.path.basename(self.archivo.name)
