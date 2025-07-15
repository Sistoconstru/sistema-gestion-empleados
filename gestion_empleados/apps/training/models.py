from django.db import models

# Create your models here.
# =============================================================================
# apps/training/models.py
# =============================================================================

import uuid
from django.db import models


class TipoCapacitacion(models.Model):
    """Tipos de capacitación"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        db_table = 'tipos_capacitacion'
        verbose_name = 'Tipo de Capacitación'
        verbose_name_plural = 'Tipos de Capacitación'
    
    def __str__(self):
        return self.nombre


class Capacitacion(models.Model):
    """Capacitaciones del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.ForeignKey(TipoCapacitacion, on_delete=models.CASCADE)
    duracion_estimada_horas = models.IntegerField()
    puntaje_aprobacion = models.IntegerField(default=70)
    intentos_maximos = models.IntegerField(default=3)
    fecha_vigencia_inicio = models.DateField()
    fecha_vigencia_fin = models.DateField(null=True, blank=True)
    version = models.CharField(max_length=10, default='1.0')
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creada_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'capacitaciones'
        unique_together = ['codigo', 'version']
        verbose_name = 'Capacitación'
        verbose_name_plural = 'Capacitaciones'
    
    def __str__(self):
        return self.nombre


class CapacitacionCargo(models.Model):
    """Relación entre capacitaciones y cargos"""
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE)
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)
    obligatoria = models.BooleanField(default=True)
    dias_plazo_completar = models.IntegerField(default=30)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    asignado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'capacitaciones_cargos'
        unique_together = ['capacitacion', 'cargo']


class ModuloCapacitacion(models.Model):
    """Módulos de una capacitación"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    orden = models.IntegerField()
    duracion_estimada_minutos = models.IntegerField()
    modulo_prerequisito = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'modulos_capacitacion'
        unique_together = ['capacitacion', 'orden']
        verbose_name = 'Módulo de Capacitación'
        verbose_name_plural = 'Módulos de Capacitación'
    
    def __str__(self):
        return f"{self.capacitacion.nombre} - {self.nombre}"


class Leccion(models.Model):
    """Lecciones de un módulo"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    modulo = models.ForeignKey(ModuloCapacitacion, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    orden = models.IntegerField()
    duracion_estimada_minutos = models.IntegerField()
    leccion_prerequisito = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'lecciones'
        unique_together = ['modulo', 'orden']
        verbose_name = 'Lección'
        verbose_name_plural = 'Lecciones'
    
    def __str__(self):
        return f"{self.modulo.nombre} - {self.nombre}"


class TipoContenido(models.Model):
    """Tipos de contenido para lecciones"""
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50, unique=True)
    extensiones_permitidas = models.CharField(max_length=100)
    mime_types = models.CharField(max_length=200)
    requiere_archivo = models.BooleanField(default=True)
    requiere_url = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'tipos_contenido'
        verbose_name = 'Tipo de Contenido'
        verbose_name_plural = 'Tipos de Contenido'
    
    def __str__(self):
        return self.nombre


class ContenidoLeccion(models.Model):
    """Contenidos de una lección"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_contenido = models.ForeignKey(TipoContenido, on_delete=models.CASCADE)
    archivo = models.FileField(upload_to='capacitaciones/', blank=True)
    url_externa = models.URLField(blank=True)
    orden = models.IntegerField()
    obligatorio = models.BooleanField(default=True)
    tiempo_minimo_visualizacion = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'contenidos_leccion'
        unique_together = ['leccion', 'orden']
        verbose_name = 'Contenido de Lección'
        verbose_name_plural = 'Contenidos de Lección'


class InscripcionCapacitacion(models.Model):
    """Inscripciones de empleados a capacitaciones"""
    ESTADOS = [
        ('no_iniciado', 'No Iniciado'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('aprobado', 'Aprobado'),
        ('reprobado', 'Reprobado'),
        ('vencido', 'Vencido'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE)
    capacitacion = models.ForeignKey(Capacitacion, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    fecha_limite = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=25, choices=ESTADOS, default='no_iniciado')
    obligatoria = models.BooleanField()
    aprobada_supervisor = models.BooleanField(default=True)
    puntaje_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tiempo_total_minutos = models.IntegerField(default=0)
    intentos_realizados = models.IntegerField(default=0)
    inscrito_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'inscripciones_capacitacion'
        unique_together = ['empleado', 'capacitacion']
        verbose_name = 'Inscripción a Capacitación'
        verbose_name_plural = 'Inscripciones a Capacitación'


class ProgresoCapacitacion(models.Model):
    """Progreso de empleados en capacitaciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscripcion = models.ForeignKey(InscripcionCapacitacion, on_delete=models.CASCADE)
    contenido = models.ForeignKey(ContenidoLeccion, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    tiempo_dedicado_segundos = models.IntegerField(default=0)
    porcentaje_visto = models.IntegerField(default=0)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    numero_visitas = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'progreso_capacitacion'
        unique_together = ['inscripcion', 'contenido']
        verbose_name = 'Progreso de Capacitación'
        verbose_name_plural = 'Progresos de Capacitación'

