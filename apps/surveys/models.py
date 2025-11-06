from django.db import models

# Create your models here.
# =============================================================================
# apps/surveys/models.py
# =============================================================================

import uuid
from django.db import models


class TipoEncuesta(models.Model):
    """Tipos de encuestas"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    obligatoria = models.BooleanField(default=False)
    anonima = models.BooleanField(default=False)
    frecuencia_dias = models.IntegerField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_encuesta'
        verbose_name = 'Tipo de Encuesta'
        verbose_name_plural = 'Tipos de Encuesta'
    
    def __str__(self):
        return self.nombre


class Encuesta(models.Model):
    """Encuestas del sistema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    instrucciones = models.TextField(blank=True)
    tipo_encuesta = models.ForeignKey(TipoEncuesta, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creada_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'encuestas'
        verbose_name = 'Encuesta'
        verbose_name_plural = 'Encuestas'
    
    def __str__(self):
        return self.nombre


class EncuestaCargo(models.Model):
    """Relación entre encuestas y cargos"""
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'encuestas_cargos'


class EncuestaArea(models.Model):
    """Relación entre encuestas y áreas"""
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    area = models.ForeignKey('organizational.AreaEmpresa', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'encuestas_areas'


class PreguntaEncuesta(models.Model):
    """Preguntas de encuestas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    tipo_pregunta = models.ForeignKey('evaluations.TipoPregunta', on_delete=models.CASCADE)
    categoria = models.CharField(max_length=100, blank=True)
    pregunta = models.TextField()
    descripcion = models.TextField(blank=True)
    obligatoria = models.BooleanField(default=True)
    orden = models.IntegerField()
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'preguntas_encuesta'
        unique_together = ['encuesta', 'orden']
        verbose_name = 'Pregunta de Encuesta'
        verbose_name_plural = 'Preguntas de Encuesta'


class OpcionEncuesta(models.Model):
    """Opciones de respuesta para encuestas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pregunta = models.ForeignKey(PreguntaEncuesta, on_delete=models.CASCADE)
    opcion = models.TextField()
    valor_numerico = models.IntegerField(null=True, blank=True)
    orden = models.IntegerField()
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'opciones_encuesta'
        unique_together = ['pregunta', 'orden']
        verbose_name = 'Opción de Encuesta'
        verbose_name_plural = 'Opciones de Encuesta'


class ParticipacionEncuesta(models.Model):
    """Participaciones en encuestas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado = models.ForeignKey('employees.Empleado', on_delete=models.SET_NULL, null=True, blank=True)  # Null para encuestas anónimas
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    tiempo_empleado_minutos = models.IntegerField(null=True, blank=True)
    completada = models.BooleanField(default=False)
    porcentaje_completado = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    dispositivo = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'participaciones_encuesta'
        unique_together = ['empleado', 'encuesta']
        verbose_name = 'Participación en Encuesta'
        verbose_name_plural = 'Participaciones en Encuesta'


class RespuestaEncuesta(models.Model):
    """Respuestas de encuestas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participacion = models.ForeignKey(ParticipacionEncuesta, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(PreguntaEncuesta, on_delete=models.CASCADE)
    opcion_seleccionada = models.ForeignKey(OpcionEncuesta, on_delete=models.SET_NULL, null=True, blank=True)
    respuesta_texto = models.TextField(blank=True)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'respuestas_encuesta'
        unique_together = ['participacion', 'pregunta']
        verbose_name = 'Respuesta de Encuesta'
        verbose_name_plural = 'Respuestas de Encuesta'

