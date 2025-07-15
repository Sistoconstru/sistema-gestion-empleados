
# =============================================================================
# apps/evaluations/models.py
# =============================================================================

import uuid
from django.db import models


class TipoPregunta(models.Model):
    """Tipos de preguntas para evaluaciones y valoraciones"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    permite_opciones = models.BooleanField(default=True)
    permite_texto_libre = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'tipos_pregunta'
        verbose_name = 'Tipo de Pregunta'
        verbose_name_plural = 'Tipos de Pregunta'
    
    def __str__(self):
        return self.nombre


class Valoracion(models.Model):
    """Valoraciones/exámenes de capacitaciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capacitacion = models.OneToOneField('training.Capacitacion', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    instrucciones = models.TextField(blank=True)
    puntaje_maximo = models.IntegerField(default=100)
    tiempo_limite_minutos = models.IntegerField(null=True, blank=True)
    mostrar_resultados_inmediatos = models.BooleanField(default=True)
    permitir_revision = models.BooleanField(default=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creada_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'valoraciones'
        verbose_name = 'Valoración'
        verbose_name_plural = 'Valoraciones'
    
    def __str__(self):
        return self.nombre


class PreguntaValoracion(models.Model):
    """Preguntas de una valoración"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    valoracion = models.ForeignKey(Valoracion, on_delete=models.CASCADE)
    tipo_pregunta = models.ForeignKey(TipoPregunta, on_delete=models.CASCADE)
    pregunta = models.TextField()
    explicacion = models.TextField(blank=True)
    puntaje = models.IntegerField()
    orden = models.IntegerField()
    obligatoria = models.BooleanField(default=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'preguntas_valoracion'
        unique_together = ['valoracion', 'orden']
        verbose_name = 'Pregunta de Valoración'
        verbose_name_plural = 'Preguntas de Valoración'


class OpcionRespuesta(models.Model):
    """Opciones de respuesta para preguntas"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pregunta = models.ForeignKey(PreguntaValoracion, on_delete=models.CASCADE)
    opcion = models.TextField()
    es_correcta = models.BooleanField(default=False)
    orden = models.IntegerField()
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'opciones_respuesta'
        unique_together = ['pregunta', 'orden']
        verbose_name = 'Opción de Respuesta'
        verbose_name_plural = 'Opciones de Respuesta'


class IntentoValoracion(models.Model):
    """Intentos de valoración por parte de empleados"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscripcion = models.ForeignKey('training.InscripcionCapacitacion', on_delete=models.CASCADE)
    numero_intento = models.IntegerField()
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    tiempo_utilizado_minutos = models.IntegerField(null=True, blank=True)
    puntaje_obtenido = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    porcentaje_acierto = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    aprobado = models.BooleanField(default=False)
    completado = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'intentos_valoracion'
        unique_together = ['inscripcion', 'numero_intento']
        verbose_name = 'Intento de Valoración'
        verbose_name_plural = 'Intentos de Valoración'


class RespuestaValoracion(models.Model):
    """Respuestas de empleados en valoraciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intento = models.ForeignKey(IntentoValoracion, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(PreguntaValoracion, on_delete=models.CASCADE)
    opcion_seleccionada = models.ForeignKey(OpcionRespuesta, on_delete=models.SET_NULL, null=True, blank=True)
    respuesta_texto = models.TextField(blank=True)
    puntaje_obtenido = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    es_correcta = models.BooleanField(default=False)
    tiempo_respuesta_segundos = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'respuestas_valoracion'
        unique_together = ['intento', 'pregunta']
        verbose_name = 'Respuesta de Valoración'
        verbose_name_plural = 'Respuestas de Valoración'


class CertificadoCapacitacion(models.Model):
    """Certificados de capacitación"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscripcion = models.OneToOneField('training.InscripcionCapacitacion', on_delete=models.CASCADE)
    numero_certificado = models.CharField(max_length=50, unique=True)
    archivo_certificado = models.FileField(upload_to='certificados/', blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    emitido_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'certificados_capacitacion'
        verbose_name = 'Certificado de Capacitación'
        verbose_name_plural = 'Certificados de Capacitación'


# Evaluaciones de Desempeño

class TipoEvaluacion(models.Model):
    """Tipos de evaluación de desempeño"""
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    dias_activacion = models.IntegerField()
    frecuencia_dias = models.IntegerField(null=True, blank=True)
    es_autoevaluacion = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tipos_evaluacion'
        verbose_name = 'Tipo de Evaluación'
        verbose_name_plural = 'Tipos de Evaluación'
    
    def __str__(self):
        return self.nombre


class EvaluacionDesempeño(models.Model):
    """Evaluaciones de desempeño"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    instrucciones = models.TextField(blank=True)
    tipo_evaluacion = models.ForeignKey(TipoEvaluacion, on_delete=models.CASCADE)
    version = models.CharField(max_length=10, default='1.0')
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creada_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'evaluaciones_desempeño'
        unique_together = ['codigo', 'version']
        verbose_name = 'Evaluación de Desempeño'
        verbose_name_plural = 'Evaluaciones de Desempeño'
    
    def __str__(self):
        return self.nombre


class EvaluacionCargo(models.Model):
    """Relación entre evaluaciones y cargos"""
    evaluacion = models.ForeignKey(EvaluacionDesempeño, on_delete=models.CASCADE)
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    asignado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'evaluaciones_cargos'
        unique_together = ['evaluacion', 'cargo']


class PreguntaEvaluacion(models.Model):
    """Preguntas de evaluación de desempeño"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluacion = models.ForeignKey(EvaluacionDesempeño, on_delete=models.CASCADE)
    tipo_pregunta = models.ForeignKey(TipoPregunta, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=100, blank=True)
    pregunta = models.TextField()
    descripcion = models.TextField(blank=True)
    peso_porcentual = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    orden = models.IntegerField()
    obligatoria = models.BooleanField(default=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'preguntas_evaluacion'
        unique_together = ['evaluacion', 'orden']
        verbose_name = 'Pregunta de Evaluación'
        verbose_name_plural = 'Preguntas de Evaluación'


class OpcionEvaluacion(models.Model):
    """Opciones de respuesta para evaluaciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pregunta = models.ForeignKey(PreguntaEvaluacion, on_delete=models.CASCADE)
    opcion = models.TextField()
    valor_numerico = models.DecimalField(max_digits=5, decimal_places=2)
    orden = models.IntegerField()
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'opciones_evaluacion'
        unique_together = ['pregunta', 'orden']
        verbose_name = 'Opción de Evaluación'
        verbose_name_plural = 'Opciones de Evaluación'


class AsignacionEvaluacion(models.Model):
    """Asignaciones de evaluaciones a empleados"""
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('vencida', 'Vencida'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado_evaluado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE, related_name='evaluaciones_recibidas')
    evaluacion = models.ForeignKey(EvaluacionDesempeño, on_delete=models.CASCADE)
    evaluador = models.ForeignKey('employees.Empleado', on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluaciones_realizadas')
    periodo_evaluacion = models.CharField(max_length=20)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    es_autoevaluacion = models.BooleanField(default=False)
    puntaje_total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    porcentaje_completado = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    asignado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'asignaciones_evaluacion'
        unique_together = ['empleado_evaluado', 'evaluacion', 'periodo_evaluacion', 'es_autoevaluacion']
        verbose_name = 'Asignación de Evaluación'
        verbose_name_plural = 'Asignaciones de Evaluación'


class RespuestaEvaluacion(models.Model):
    """Respuestas de evaluaciones de desempeño"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asignacion = models.ForeignKey(AsignacionEvaluacion, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(PreguntaEvaluacion, on_delete=models.CASCADE)
    opcion_seleccionada = models.ForeignKey(OpcionEvaluacion, on_delete=models.SET_NULL, null=True, blank=True)
    respuesta_texto = models.TextField(blank=True)
    puntaje_obtenido = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    comentarios_evaluador = models.TextField(blank=True)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'respuestas_evaluacion'
        unique_together = ['asignacion', 'pregunta']
        verbose_name = 'Respuesta de Evaluación'
        verbose_name_plural = 'Respuestas de Evaluación'


class ResultadoEvaluacion(models.Model):
    """Resultados consolidados de evaluaciones"""
    NIVELES_DESEMPEÑO = [
        ('excelente', 'Excelente'),
        ('sobresaliente', 'Sobresaliente'),
        ('satisfactorio', 'Satisfactorio'),
        ('mejorable', 'Mejorable'),
        ('insatisfactorio', 'Insatisfactorio'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asignacion = models.OneToOneField(AsignacionEvaluacion, on_delete=models.CASCADE)
    puntaje_final = models.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_obtenido = models.DecimalField(max_digits=5, decimal_places=2)
    nivel_desempeño = models.CharField(max_length=20, choices=NIVELES_DESEMPEÑO)
    aspectos_positivos = models.TextField()
    areas_mejora = models.TextField()
    comentarios_generales = models.TextField(blank=True)
    metas_siguientes = models.TextField(blank=True)
    recomendaciones = models.TextField(blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    generado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'resultados_evaluacion'
        verbose_name = 'Resultado de Evaluación'
        verbose_name_plural = 'Resultados de Evaluación'


class PlanAccion(models.Model):
    """Planes de acción derivados de evaluaciones"""
    PRIORIDADES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resultado_evaluacion = models.ForeignKey(ResultadoEvaluacion, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion_accion = models.TextField()
    objetivo = models.TextField(blank=True)
    responsable = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE, related_name='planes_responsable')
    supervisor = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE, related_name='planes_supervisor')
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES)
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField()
    fecha_seguimiento = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    porcentaje_avance = models.IntegerField(default=0)
    recursos_necesarios = models.TextField(blank=True)
    comentarios = models.TextField(blank=True)
    evidencias = models.FileField(upload_to='planes_accion/', blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'planes_accion'
        verbose_name = 'Plan de Acción'
        verbose_name_plural = 'Planes de Acción'

