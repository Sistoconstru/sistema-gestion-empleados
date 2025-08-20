from django.db import models

# Create your models here.
# =============================================================================
# apps/training/models.py
# =============================================================================

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TipoCapacitacion(models.Model):
    """Tipos de capacitación"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    permite_inscripcion_libre = models.BooleanField(default=False, help_text="Permite autogestión por empleados")
    requiere_aprobacion_supervisor = models.BooleanField(default=False, help_text="Requiere aprobación del supervisor")
    
    class Meta:
        db_table = 'tipos_capacitacion'
        verbose_name = 'Tipo de Capacitación'
        verbose_name_plural = 'Tipos de Capacitación'
    
    def __str__(self):
        return self.nombre

class ProveedorExterno(models.Model):
    """Proveedores externos de capacitación"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    sitio_web = models.URLField(blank=True)
    contacto_email = models.EmailField(blank=True)
    contacto_telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'proveedores_externos'
        verbose_name = 'Proveedor Externo'
        verbose_name_plural = 'Proveedores Externos'
    
    def __str__(self):
        return self.nombre

class Capacitacion(models.Model):
    """Capacitaciones del sistema"""
    
    NIVELES_DIFICULTAD = [
        ('basico', 'Básico'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.ForeignKey(TipoCapacitacion, on_delete=models.CASCADE)
    
    # Configuración básica
    duracion_estimada_horas = models.IntegerField(validators=[MinValueValidator(1)])
    nivel_dificultad = models.CharField(max_length=20, choices=NIVELES_DIFICULTAD, default='basico')
    puntaje_aprobacion = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    intentos_maximos = models.IntegerField(default=3, validators=[MinValueValidator(1)])
    
    # Vigencia
    fecha_vigencia_inicio = models.DateField()
    fecha_vigencia_fin = models.DateField(null=True, blank=True)
    version = models.CharField(max_length=10, default='1.0')
    
    # Proveedor externo (NUEVOS CAMPOS)
    proveedor_externo = models.ForeignKey(
        ProveedorExterno, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Solo para capacitaciones externas"
    )
    url_inscripcion_externa = models.URLField(
        blank=True, 
        help_text="URL para inscripción directa en el proveedor"
    )
    requiere_certificado_externo = models.BooleanField(
        default=False, 
        help_text="Requiere subir certificado del proveedor al finalizar"
    )
    permite_autocompletado = models.BooleanField(
        default=False, 
        help_text="El empleado puede marcar como completada sin evaluación"
    )
    
    # Gamificación y costos (NUEVOS CAMPOS)
    costo_inscripcion = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Costo en pesos colombianos"
    )
    puntos_gamificacion = models.IntegerField(
        default=0,
        help_text="Puntos que otorga al completar",
        validators=[MinValueValidator(0)]
    )
    
    # Estado
    activa = models.BooleanField(
        default=True, 
        help_text="Indica si la capacitación está disponible para inscripción"
    )
    
    # Configuración avanzada (NUEVOS CAMPOS)
    requiere_prerequisitos = models.BooleanField(default=False)
    permite_certificacion_manual = models.BooleanField(
        default=True,
        help_text="Permite que administrador certifique manualmente"
    )
    visible_en_catalogo = models.BooleanField(
        default=True,
        help_text="Visible en catálogo para empleados"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creada_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'capacitaciones'
        unique_together = ['codigo', 'version']
        verbose_name = 'Capacitación'
        verbose_name_plural = 'Capacitaciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    # MÉTODOS HELPER (NUEVOS)
    def es_externa(self):
        """Verifica si es una capacitación externa"""
        return self.proveedor_externo is not None
    
    def es_obligatoria_por_cargo(self):
        """Verifica si es obligatoria para algún cargo"""
        return self.capacitacioncargo_set.filter(obligatoria=True).exists()
    
    def requiere_modulos(self):
        """Verifica si requiere estructura de módulos"""
        return not self.es_externa()
    
    def get_duracion_display(self):
        """Formatear duración para mostrar"""
        if self.duracion_estimada_horas == 1:
            return "1 hora"
        elif self.duracion_estimada_horas < 8:
            return f"{self.duracion_estimada_horas} horas"
        else:
            dias = self.duracion_estimada_horas // 8
            horas_restantes = self.duracion_estimada_horas % 8
            if horas_restantes == 0:
                return f"{dias} día{'s' if dias > 1 else ''}"
            else:
                return f"{dias} día{'s' if dias > 1 else ''} y {horas_restantes} hora{'s' if horas_restantes > 1 else ''}"
    
    def get_costo_display(self):
        """Formatear costo para mostrar"""
        if self.costo_inscripcion == 0:
            return "Gratuita"
        else:
            return f"${self.costo_inscripcion:,.0f} COP"

class CapacitacionPrerequisito(models.Model):
    """Prerequisitos entre capacitaciones"""
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE, related_name='prerequisitos')
    capacitacion_prerequisito = models.ForeignKey(Capacitacion, on_delete=models.CASCADE, related_name='es_prerequisito_de')
    obligatorio = models.BooleanField(default=True, help_text="Si es falso, es solo recomendado")
    
    class Meta:
        db_table = 'capacitaciones_prerequisitos'
        unique_together = ['capacitacion', 'capacitacion_prerequisito']
        verbose_name = 'Prerequisito de Capacitación'
        verbose_name_plural = 'Prerequisitos de Capacitación'

class CapacitacionCargo(models.Model):
    """Relación entre capacitaciones y cargos - ACTUALIZADO"""
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE)
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)
    obligatoria = models.BooleanField(default=True)
    dias_plazo_completar = models.IntegerField(
        default=30,
        help_text="Días que tiene el empleado para completar desde la asignación"
    )
    prioridad = models.IntegerField(
        default=1,
        help_text="1=Alta, 2=Media, 3=Baja",
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    asignado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'capacitaciones_cargos'
        unique_together = ['capacitacion', 'cargo']
        verbose_name = 'Capacitación por Cargo'
        verbose_name_plural = 'Capacitaciones por Cargo'
    
    def get_prioridad_display(self):
        prioridades = {1: 'Alta', 2: 'Media', 3: 'Baja'}
        return prioridades.get(self.prioridad, 'Media')

class ModuloCapacitacion(models.Model):
    """Módulos de una capacitación - MEJORADO"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    orden = models.IntegerField()
    duracion_estimada_minutos = models.IntegerField()
    
    # Configuración (NUEVOS CAMPOS)
    modulo_prerequisito = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Módulo que debe completarse antes de este"
    )
    puntaje_minimo_aprobar = models.IntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    permite_repetir = models.BooleanField(default=True)
    
    # Estado
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'modulos_capacitacion'
        unique_together = ['capacitacion', 'orden']
        verbose_name = 'Módulo de Capacitación'
        verbose_name_plural = 'Módulos de Capacitación'
        ordering = ['capacitacion', 'orden']
    
    def __str__(self):
        return f"{self.capacitacion.nombre} - {self.nombre}"

class Leccion(models.Model):
    """Lecciones de un módulo - MEJORADO"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modulo = models.ForeignKey(ModuloCapacitacion, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    orden = models.IntegerField()
    duracion_estimada_minutos = models.IntegerField()
    
    # Configuración (NUEVOS CAMPOS)
    leccion_prerequisito = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    tiempo_minimo_visualizacion = models.IntegerField(
        default=0,
        help_text="Tiempo mínimo en segundos que debe ver la lección"
    )
    requiere_completar_anterior = models.BooleanField(
        default=True,
        help_text="Debe completar la lección anterior para acceder"
    )
    
    # Estado
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'lecciones'
        unique_together = ['modulo', 'orden']
        verbose_name = 'Lección'
        verbose_name_plural = 'Lecciones'
        ordering = ['modulo', 'orden']
    
    def __str__(self):
        return f"{self.modulo.nombre} - {self.nombre}"

class TipoContenido(models.Model):
    """Tipos de contenido para lecciones - MEJORADO"""
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    extensiones_permitidas = models.CharField(max_length=100, blank=True)
    mime_types = models.CharField(max_length=200, blank=True)
    requiere_archivo = models.BooleanField(default=True)
    requiere_url = models.BooleanField(default=False)
    icono_fa = models.CharField(max_length=50, default='fas fa-file', help_text="Clase de FontAwesome")
    color_hex = models.CharField(max_length=7, default='#6c757d', help_text="Color hexadecimal")
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_contenido'
        verbose_name = 'Tipo de Contenido'
        verbose_name_plural = 'Tipos de Contenido'
    
    def __str__(self):
        return self.nombre

class ContenidoLeccion(models.Model):
    """Contenidos de una lección - MEJORADO"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_contenido = models.ForeignKey(TipoContenido, on_delete=models.CASCADE)
    
    # Archivos y URLs
    archivo = models.FileField(upload_to='capacitaciones/contenido/', blank=True)
    url_externa = models.URLField(blank=True)
    contenido_texto = models.TextField(blank=True, help_text="Para contenido de texto directo")
    
    # Configuración
    orden = models.IntegerField()
    obligatorio = models.BooleanField(default=True)
    tiempo_minimo_visualizacion = models.IntegerField(
        default=0,
        help_text="Tiempo mínimo en segundos"
    )
    permite_descarga = models.BooleanField(default=True)
    
    # Metadatos
    tamaño_archivo_mb = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey('authentication.Usuario',
    on_delete=models.SET_NULL,
    null=True,
    blank=True)
    
    class Meta:
        db_table = 'contenidos_leccion'
        unique_together = ['leccion', 'orden']
        verbose_name = 'Contenido de Lección'
        verbose_name_plural = 'Contenidos de Lección'
        ordering = ['leccion', 'orden']
    
    def __str__(self):
        return f"{self.leccion.nombre} - {self.nombre}"

class InscripcionCapacitacion(models.Model):
    """Inscripciones de empleados a capacitaciones - MEJORADO"""
    ESTADOS = [
        ('no_iniciado', 'No Iniciado'),
        ('pendiente_validacion', 'Pendiente de Validación'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('aprobado', 'Aprobado'),
        ('reprobado', 'Reprobado'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE)
    
    # Fechas
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    # Estado y configuración
    estado = models.CharField(max_length=25, choices=ESTADOS, default='no_iniciado')
    obligatoria = models.BooleanField(default=False)
    aprobada_supervisor = models.BooleanField(default=True)
    
    # Resultados
    puntaje_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tiempo_total_minutos = models.IntegerField(default=0)
    intentos_realizados = models.IntegerField(default=0)
    porcentaje_completado = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Certificación externa (NUEVOS CAMPOS)
    certificado_externo = models.FileField(
        upload_to='capacitaciones/certificados/', 
        blank=True,
        help_text="Certificado obtenido del proveedor externo"
    )
    fecha_certificado_externo = models.DateField(null=True, blank=True)
    validado_por_admin = models.BooleanField(default=False)
    
    # Observaciones
    observaciones_empleado = models.TextField(blank=True)
    observaciones_supervisor = models.TextField(blank=True)
    observaciones_admin = models.TextField(blank=True)
    
    # Usuarios relacionados
    inscrito_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE, related_name='inscripciones_creadas')
    aprobado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='inscripciones_aprobadas')
    
    class Meta:
        db_table = 'inscripciones_capacitacion'
        unique_together = ['empleado', 'capacitacion']
        verbose_name = 'Inscripción a Capacitación'
        verbose_name_plural = 'Inscripciones a Capacitación'
        ordering = ['-fecha_inscripcion']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.capacitacion.nombre}"
    
    def get_estado_color(self):
        """Color para badges según estado"""
        colores = {
            'no_iniciado': 'secondary',
            'en_progreso': 'warning',
            'completado': 'info',
            'aprobado': 'success',
            'reprobado': 'danger',
            'vencido': 'danger',
            'cancelado': 'dark'
        }
        return colores.get(self.estado, 'secondary')

class ProgresoCapacitacion(models.Model):
    """Progreso de empleados en capacitaciones - MEJORADO"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscripcion = models.ForeignKey(InscripcionCapacitacion, on_delete=models.CASCADE)
    contenido = models.ForeignKey(ContenidoLeccion, on_delete=models.CASCADE)
    
    # Estado de progreso
    completado = models.BooleanField(default=False)
    tiempo_dedicado_segundos = models.IntegerField(default=0)
    porcentaje_visto = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Fechas de seguimiento
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    fecha_ultimo_acceso = models.DateTimeField(auto_now=True)
    
    # Estadísticas
    numero_visitas = models.IntegerField(default=0)
    tiempo_promedio_por_visita = models.IntegerField(default=0)
    
    # Interacciones (NUEVOS CAMPOS)
    marcadores = models.JSONField(default=list, blank=True, help_text="Marcadores de tiempo en videos")
    notas_empleado = models.TextField(blank=True)
    puntuacion_contenido = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Puntuación de 1 a 5 del empleado"
    )
    
    class Meta:
        db_table = 'progreso_capacitacion'
        unique_together = ['inscripcion', 'contenido']
        verbose_name = 'Progreso de Capacitación'
        verbose_name_plural = 'Progresos de Capacitación'


