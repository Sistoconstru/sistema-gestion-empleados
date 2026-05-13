# =============================================================================
# apps/evaluations/models.py
# =============================================================================

import uuid
from django.db import models

# ===================== MODELOS DE PREGUNTAS Y VALORACIONES =====================

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

# ===================== EVALUACIONES DE DESEMPEÑO =====================

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
    ESTADO_CHOICES = [
        ('programada', 'Programada'),
        ('activa', 'Activa'),
        ('finalizada', 'Finalizada'),
    ]

    evaluacion = models.ForeignKey(EvaluacionDesempeño, on_delete=models.CASCADE)
    cargo = models.ForeignKey('organizational.Cargo', on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    asignado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)

    # Control de activación
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='programada',
        help_text='La evaluación se asigna a empleados solo cuando está Activa'
    )
    fecha_activacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha en que se activó la evaluación y se asignó a empleados'
    )
    fecha_vencimiento_planeada = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha límite para completar la evaluación'
    )
    dias_para_completar = models.IntegerField(
        default=30,
        help_text='Días que tienen los empleados para completar la evaluación'
    )
    activada_por = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_cargo_activadas',
        help_text='Usuario que activó la evaluación'
    )
    periodo_a_evaluar = models.CharField(
        max_length=50,
        blank=True,
        help_text='Período a evaluar (ej: 2025, 2025-2026, etc.)'
    )

    class Meta:
        db_table = 'evaluaciones_cargos'
        unique_together = ['evaluacion', 'cargo']

    def __str__(self):
        return f"{self.evaluacion.nombre} → {self.cargo.nombre} ({self.get_estado_display()})"

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
        ('completada', 'Completada'),  # Evaluación terminada, seguimientos pendientes
        ('requiere_correccion', 'Requiere Corrección'),  # Desaprobada por RRHH, necesita corrección
        ('finalizada', 'Finalizada'),  # TODO el proceso completo (evaluación + seguimientos)
        ('vencida', 'Vencida'),
    ]
    
    ESTADOS_APROBACION = [
        ('pendiente_aprobacion', 'Pendiente de Aprobación'),
        ('aprobada', 'Aprobada'),
        ('desaprobada', 'Desaprobada'),
        ('requiere_revision', 'Requiere Revisión'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    empleado_evaluado = models.ForeignKey('employees.Empleado', on_delete=models.CASCADE, related_name='evaluaciones_recibidas')
    evaluacion = models.ForeignKey(EvaluacionDesempeño, on_delete=models.CASCADE)
    evaluador = models.ForeignKey('employees.Empleado', on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluaciones_realizadas')
    periodo_evaluacion = models.CharField(max_length=100)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    es_autoevaluacion = models.BooleanField(default=False)
    puntaje_total = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    porcentaje_completado = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    asignado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE)
    
    # Campos de aprobación administrativa
    estado_aprobacion = models.CharField(max_length=30, choices=ESTADOS_APROBACION, null=True, blank=True)
    aprobada_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluaciones_aprobadas')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    comentarios_aprobacion = models.TextField(blank=True)
    recomendacion_continuidad = models.CharField(max_length=20, choices=[('continua', 'Continúa'), ('no_continua', 'No Continúa')], null=True, blank=True)
    aspectos_mejora_generados = models.TextField(blank=True, help_text='Aspectos de mejora generados automáticamente')
    observaciones = models.TextField(blank=True)

    # Campo de Seguridad y Salud en el Trabajo (SST) - Solo para evaluaciones anuales
    USO_EPP_CHOICES = [
        ('correcto', 'Los usa correctamente y promueve su uso'),
        ('a_veces', 'A veces no los usa adecuadamente'),
        ('nunca', 'No los usa o no promueve su uso'),
    ]
    uso_epp_sst = models.CharField(
        max_length=20,
        choices=USO_EPP_CHOICES,
        blank=True,
        verbose_name='Uso de Elementos de Protección Personal (EPP)',
        help_text='Observación de SST - No computa en el puntaje de la evaluación'
    )

    class Meta:
        db_table = 'asignaciones_evaluacion'
        unique_together = ['empleado_evaluado', 'evaluacion', 'periodo_evaluacion', 'es_autoevaluacion']
        verbose_name = 'Asignación de Evaluación'
        verbose_name_plural = 'Asignaciones de Evaluación'

    @property
    def planmejorapredefinido(self):
        """
        Propiedad para mantener compatibilidad con templates existentes.
        Devuelve el primer plan de mejora asociado a esta asignación.
        """
        return self.planes_mejora.first() if self.planes_mejora.exists() else None

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


class PlanMejoraPredefinido(models.Model):
    """Planes de mejora generados automáticamente con respuestas predefinidas"""
    ESTADOS = [
        ('pendiente_aprobacion', 'Pendiente de Aprobación'),
        ('aprobado', 'Aprobado'),
        ('en_seguimiento', 'En Seguimiento'),
        ('completado', 'Completado'),
        ('rechazado', 'Rechazado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asignacion_evaluacion = models.ForeignKey(AsignacionEvaluacion, on_delete=models.CASCADE, related_name='planes_mejora')
    
    # Respuestas predefinidas generadas automáticamente
    plan_mejora = models.TextField(help_text="Plan de mejora generado automáticamente basado en las respuestas")
    
    # Estado y aprobación
    estado = models.CharField(max_length=25, choices=ESTADOS, default='pendiente_aprobacion')
    
    # Aceptación del empleado
    aceptado_por_empleado = models.BooleanField(default=False, help_text="Indica si el empleado ha aceptado el plan")
    fecha_aceptacion_empleado = models.DateTimeField(null=True, blank=True, help_text="Fecha en que el empleado aceptó el plan")

    # Rechazo del empleado
    rechazado_por_empleado = models.BooleanField(default=False, help_text="Indica si el empleado ha rechazado el plan")
    fecha_rechazo_empleado = models.DateTimeField(null=True, blank=True, help_text="Fecha en que el empleado rechazó el plan")
    motivo_rechazo_empleado = models.TextField(blank=True, help_text="Motivo por el cual el empleado rechazó el plan")

    # Revisión de Gestión Humana (cuando empleado rechaza)
    en_revision_rrhh = models.BooleanField(default=False, help_text="Indica si está en revisión por RRHH tras rechazo del empleado")
    decision_rrhh = models.CharField(
        max_length=30,
        blank=True,
        choices=[
            ('aprobar_plan_original', 'Aprobar Plan Original'),
            ('solicitar_nueva_evaluacion', 'Solicitar Nueva Evaluación'),
            ('modificar_plan', 'Modificar Plan'),
        ],
        help_text="Decisión de RRHH sobre el plan rechazado por el empleado"
    )
    comentarios_decision_rrhh = models.TextField(blank=True, help_text="Comentarios de RRHH sobre la decisión tomada")
    fecha_decision_rrhh = models.DateTimeField(null=True, blank=True, help_text="Fecha de la decisión de RRHH")
    decidido_por_rrhh = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='decisiones_rrhh_planes',
        help_text="Usuario de RRHH que tomó la decisión"
    )

    # Fechas de creación y gestión
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)

    # Usuarios involucrados
    generado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE, related_name='planes_generados')
    aprobado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='planes_aprobados')

    # Comentarios del proceso
    comentarios_aprobacion = models.TextField(blank=True, help_text="Comentarios del supervisor durante la aprobación")
    comentarios_seguimiento = models.TextField(blank=True, help_text="Comentarios del seguimiento")
    
    class Meta:
        db_table = 'planes_mejora_predefinidos'
        verbose_name = 'Plan de Mejora Predefinido'
        verbose_name_plural = 'Planes de Mejora Predefinidos'
    
    def __str__(self):
        return f"Plan {self.asignacion_evaluacion.empleado_evaluado.nombre_completo} - {self.get_estado_display()}"


class SeguimientoBimensual(models.Model):
    """Seguimiento bimensual automático de planes de mejora"""
    ESTADOS_SEGUIMIENTO = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('atrasado', 'Atrasado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_mejora = models.ForeignKey(PlanMejoraPredefinido, on_delete=models.CASCADE, related_name='seguimientos')
    
    # Información del bimestre
    numero_bimestre = models.IntegerField(help_text="1, 2, 3 (primer, segundo, tercer bimestre)")
    fecha_limite = models.DateField(help_text="Fecha límite para completar este seguimiento")
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    # Estado del seguimiento
    estado = models.CharField(max_length=15, choices=ESTADOS_SEGUIMIENTO, default='pendiente')
    
    # Campos que se marcan durante el seguimiento
    avance_satisfactorio = models.BooleanField(null=True, blank=True, help_text="¿El avance es satisfactorio?")
    observaciones = models.TextField(blank=True, help_text="Observaciones del seguimiento")
    
    # Usuario que realiza el seguimiento
    completado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'seguimientos_bimensuales'
        unique_together = ['plan_mejora', 'numero_bimestre']
        verbose_name = 'Seguimiento Bimensual'
        verbose_name_plural = 'Seguimientos Bimensuales'
        ordering = ['plan_mejora', 'numero_bimestre']
    
    def __str__(self):
        return f"Seguimiento {self.numero_bimestre}° - {self.plan_mejora}"
    
    @property
    def esta_vencido(self):
        """Verifica si el seguimiento está vencido"""
        from django.utils import timezone
        return timezone.now().date() > self.fecha_limite and self.estado == 'pendiente'


class EvaluacionFinal(models.Model):
    """Evaluación final después de los 3 bimestres de seguimiento"""
    RESULTADOS = [
        ('exitoso', 'Exitoso'),
        ('parcialmente_exitoso', 'Parcialmente Exitoso'),
        ('no_exitoso', 'No Exitoso'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_mejora = models.OneToOneField(PlanMejoraPredefinido, on_delete=models.CASCADE, related_name='evaluacion_final')

    # Resultado final
    resultado = models.CharField(max_length=25, choices=RESULTADOS)
    conclusion = models.TextField(help_text="Conclusión final del evaluador sobre el plan de mejora")

    # Fechas y usuario
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)
    evaluado_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE, related_name='evaluaciones_finales_realizadas')

    # Aceptación por parte del empleado
    aceptado_por_empleado = models.BooleanField(default=False, help_text="Si el empleado aceptó la evaluación final")
    fecha_aceptacion_empleado = models.DateTimeField(null=True, blank=True, help_text="Fecha en que el empleado aceptó")

    rechazado_por_empleado = models.BooleanField(default=False, help_text="Si el empleado rechazó la evaluación final")
    fecha_rechazo_empleado = models.DateTimeField(null=True, blank=True, help_text="Fecha en que el empleado rechazó")
    motivo_rechazo_empleado = models.TextField(blank=True, default='', help_text="Motivo del rechazo por parte del empleado")

    # Validación de Gestión Humana (solo cuando hay rechazo)
    en_revision_rrhh = models.BooleanField(default=False, help_text="Si está en revisión por Gestión Humana")
    validado_por_rrhh = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluaciones_finales_validadas',
        help_text="Usuario de RRHH que validó la evaluación final"
    )
    fecha_validacion_rrhh = models.DateTimeField(null=True, blank=True, help_text="Fecha de validación por RRHH")
    comentarios_rrhh = models.TextField(blank=True, default='', help_text="Comentarios de RRHH sobre la resolución")

    class Meta:
        db_table = 'evaluaciones_finales'
        verbose_name = 'Evaluación Final'
        verbose_name_plural = 'Evaluaciones Finales'

    def __str__(self):
        return f"Evaluación Final - {self.plan_mejora} - {self.get_resultado_display()}"

    @property
    def esta_pendiente_aceptacion(self):
        """Verifica si está pendiente de aceptación del empleado"""
        return not self.aceptado_por_empleado and not self.rechazado_por_empleado

    @property
    def fue_aceptada(self):
        """Verifica si fue aceptada por el empleado"""
        return self.aceptado_por_empleado

    @property
    def fue_rechazada(self):
        """Verifica si fue rechazada por el empleado"""
        return self.rechazado_por_empleado

    @property
    def necesita_validacion_rrhh(self):
        """Verifica si necesita validación de RRHH (fue rechazada y aún no validada)"""
        return self.rechazado_por_empleado and self.en_revision_rrhh and not self.validado_por_rrhh

