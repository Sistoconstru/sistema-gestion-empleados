from django.db import models

# Create your models here.
# =============================================================================
# apps/training/models.py
# =============================================================================

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from custom_storage.media import MediaStorage
from .utils import (
    get_certificado_externo_upload_path,
    get_certificado_generado_upload_path,
    get_plantilla_logo_upload_path,
    get_plantilla_firma_upload_path,
    get_plantilla_firma_rrhh_upload_path,
    get_plantilla_fondo_upload_path
)

User = get_user_model()

class TipoPreguntaQuiz(models.TextChoices):
    MULTIPLE = 'multiple', 'Selección Múltiple'
    VERDADERO_FALSO = 'verdadero_falso', 'Verdadero/Falso'

class QuizLeccion(models.Model):
    """Evaluación de una lección"""
    leccion = models.OneToOneField('Leccion', on_delete=models.CASCADE, related_name='evaluacion')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    porcentaje_aprobacion = models.PositiveIntegerField(
        default=70,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Porcentaje mínimo para aprobar"
    )
    tiempo_limite = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Tiempo límite en minutos. Dejar en blanco si no hay límite"
    )
    intentos_maximos = models.PositiveIntegerField(
        default=3,
        help_text="Número máximo de intentos permitidos. 0 para intentos ilimitados"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'training_evaluaciones'
        verbose_name = 'Evaluación'
        verbose_name_plural = 'Evaluaciones'

    def __str__(self):
        return f"Evaluación: {self.titulo}"
        
    def esta_aprobada(self, usuario=None):
        """Verifica si el usuario ha aprobado esta evaluación"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f'Verificando aprobación de evaluación {self.titulo} para usuario {usuario}')
        if not usuario:
            logger.info('No se proporcionó usuario, retornando False')
            return False
            
        aprobado = IntentoQuiz.objects.filter(
            quiz=self,
            usuario=usuario,
            aprobado=True
        ).exists()
        
        logger.info(f'Evaluación {self.titulo}: {"aprobada" if aprobado else "no aprobada"} por usuario {usuario}')
        return aprobado

class PreguntaQuiz(models.Model):
    """Pregunta de un quiz de lección"""
    quiz = models.ForeignKey(QuizLeccion, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField()
    tipo = models.CharField(
        max_length=20,
        choices=TipoPreguntaQuiz.choices,
        default=TipoPreguntaQuiz.MULTIPLE
    )
    puntaje = models.PositiveIntegerField(default=1)
    from custom_storage.media import MediaStorage
    imagen = models.ImageField(
        upload_to='evaluaciones/preguntas/',
        storage=MediaStorage(),
        null=True,
        blank=True
    )
    explicacion = models.TextField(
        blank=True,
        help_text="Explicación que se mostrará después de responder"
    )
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'training_preguntas_quiz'
        verbose_name = 'Pregunta de Quiz'
        verbose_name_plural = 'Preguntas de Quiz'
        ordering = ['orden']

    def __str__(self):
        return f"Pregunta {self.orden}: {self.texto[:50]}..."

class OpcionPreguntaQuiz(models.Model):
    """Opción para una pregunta de quiz"""
    pregunta = models.ForeignKey(PreguntaQuiz, on_delete=models.CASCADE, related_name='opciones')
    texto = models.TextField()
    es_correcta = models.BooleanField(default=False)
    retroalimentacion = models.TextField(
        blank=True,
        help_text="Retroalimentación específica para esta opción"
    )
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'training_opciones_quiz'
        verbose_name = 'Opción de Quiz'
        verbose_name_plural = 'Opciones de Quiz'
        ordering = ['orden']

    def __str__(self):
        return f"Opción {self.orden}: {self.texto[:50]}..."

class IntentoQuiz(models.Model):
    """Registro de un intento de quiz por parte de un usuario"""
    quiz = models.ForeignKey(QuizLeccion, on_delete=models.CASCADE, related_name='intentos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='intentos_quiz')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    puntaje_obtenido = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True
    )
    tiempo_utilizado = models.PositiveIntegerField(
        null=True,
        help_text="Tiempo utilizado en segundos"
    )
    aprobado = models.BooleanField(null=True)

    class Meta:
        db_table = 'training_intentos_quiz'
        verbose_name = 'Intento de Quiz'
        verbose_name_plural = 'Intentos de Quiz'

    def __str__(self):
        return f"Intento de {self.usuario.username} - {self.fecha_inicio}"

class RespuestaQuiz(models.Model):
    """Respuesta del usuario a una pregunta del quiz"""
    intento = models.ForeignKey(IntentoQuiz, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(PreguntaQuiz, on_delete=models.CASCADE)
    opcion_seleccionada = models.ForeignKey(
        OpcionPreguntaQuiz,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    es_correcta = models.BooleanField(null=True)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'training_respuestas_quiz'
        verbose_name = 'Respuesta de Quiz'
        verbose_name_plural = 'Respuestas de Quiz'

    def __str__(self):
        return f"Respuesta de {self.intento.usuario.username} a {self.pregunta}"

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

    MODALIDAD_CHOICES = [
        ('online', 'Online / Autoservicio'),
        ('presencial', 'Presencial'),
        ('mixta', 'Mixta (presencial + online)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.ForeignKey(TipoCapacitacion, on_delete=models.CASCADE)
    modalidad = models.CharField(
        max_length=15, choices=MODALIDAD_CHOICES, default='online',
        help_text=(
            "Presencial: se dicta en aula/sitio en una fecha programada (sesiones). "
            "Online: contenido en la plataforma. "
            "Mixta: combina ambas."
        ),
    )
    url_reunion = models.URLField(
        blank=True,
        verbose_name="Link de asistencia virtual (opcional)",
        help_text=(
            "URL de Meet, Zoom o similar para empleados que no puedan asistir "
            "presencialmente. Aplica a todas las sesiones de este curso."
        ),
    )

    # Configuración básica
    duracion_estimada_horas = models.IntegerField(validators=[MinValueValidator(1)])
    nivel_dificultad = models.CharField(max_length=20, choices=NIVELES_DIFICULTAD, default='basico')
    puntaje_aprobacion = models.IntegerField(default=70, validators=[MinValueValidator(0), MaxValueValidator(100)])
    intentos_maximos = models.IntegerField(default=3, validators=[MinValueValidator(1)])
    emite_certificado = models.BooleanField(
        default=True,
        verbose_name="Emite certificado al aprobar",
        help_text=(
            "Si está activo, al aprobar el curso se genera el PDF de certificado "
            "automáticamente. Para capacitaciones obligatorias o de inducción se "
            "suele desactivar; actívalo manualmente cuando sí se requiera evidencia "
            "(SST, compliance, etc.)."
        ),
    )
    
    # Vigencia
    fecha_vigencia_inicio = models.DateField()
    fecha_vigencia_fin = models.DateField(null=True, blank=True)
    version = models.CharField(max_length=10, default='1.0')
    
    # Capacitaciones Externas (SIMPLIFICADO)
    es_capacitacion_externa = models.BooleanField(
        default=False,
        verbose_name="Es capacitación externa",
        help_text="Marcar si es ofrecida por un proveedor externo"
    )
    url_curso_externo = models.URLField(
        blank=True,
        verbose_name="URL del curso externo",
        help_text="URL donde el empleado puede ver el contenido del curso externo"
    )
    nombre_proveedor = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre del proveedor",
        help_text="Nombre del proveedor externo (ej: Coursera, Udemy, LinkedIn Learning)"
    )
    requiere_certificado_externo = models.BooleanField(
        default=True,
        verbose_name="Requiere certificado",
        help_text="El empleado debe presentar certificado de aprobación"
    )

    # Campos antiguos (mantener por compatibilidad)
    proveedor_externo = models.ForeignKey(
        ProveedorExterno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="(Obsoleto) Solo para capacitaciones externas"
    )
    url_inscripcion_externa = models.URLField(
        blank=True,
        help_text="(Obsoleto) URL para inscripción directa en el proveedor"
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
        # Priorizar el nuevo campo booleano
        if self.es_capacitacion_externa:
            return True
        # Mantener compatibilidad con el campo antiguo
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

    def __str__(self):
        return f"{self.capacitacion.nombre} → {self.cargo.nombre}"


class ModuloCapacitacion(models.Model):
    def esta_completado(self, inscripcion=None):
        """Verifica si el módulo está completado: todas las lecciones obligatorias completadas para la inscripción dada."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[Modulo.esta_completado] Módulo: {self.nombre} | Inscripción: {inscripcion}")
        if not inscripcion:
            logger.info("[Modulo.esta_completado] Sin inscripción, retorna False")
            return False

        lecciones = self.leccion_set.filter(activa=True)
        for leccion in lecciones:
            completada = leccion.esta_completada(inscripcion=inscripcion)
            logger.info(f"[Modulo.esta_completado] Lección: {leccion.nombre} | Completada: {completada}")
            if not completada:
                logger.info(f"[Modulo.esta_completado] Falta completar lección: {leccion.nombre}")
                return False
        logger.info(f"[Modulo.esta_completado] Módulo COMPLETADO: {self.nombre}")
        return True
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

    def esta_bloqueado_por_prerequisito(self, inscripcion=None):
        """Verifica si el módulo está bloqueado por su prerrequisito para una inscripción dada"""
        # Si no tiene prerequisito (es None o está vacío), no está bloqueado
        if self.modulo_prerequisito is None:
            return False

        # Verificar si el módulo prerequisito está completado para la inscripción
        contenidos_prerequisito = self.modulo_prerequisito.leccion_set.values_list(
            'contenidoleccion__id', flat=True
        ).filter(activa=True)

        # Si el prerequisito no tiene contenidos, no está bloqueado
        if not contenidos_prerequisito.exists():
            return False

        if not inscripcion:
            return True  # Si no se pasa inscripción, se asume bloqueado

        contenidos_completados = ProgresoCapacitacion.objects.filter(
            inscripcion=inscripcion,
            contenido_id__in=contenidos_prerequisito,
            completado=True
        ).count()

        # Está bloqueado si no se han completado todos los contenidos del prerequisito
        return contenidos_completados < contenidos_prerequisito.count()
    
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
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Prerrequisitos
    leccion_prerequisito = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        help_text="Lección que debe completarse antes de esta"
    )

    def esta_bloqueada_por_prerequisito(self, inscripcion=None):
        """Verifica si la lección está bloqueada por su prerrequisito para una inscripción dada"""
        # Si el módulo está bloqueado, la lección también lo está
        if self.modulo.esta_bloqueado_por_prerequisito(inscripcion):
            return True

        if not self.leccion_prerequisito:
            return False

        # Verificar si la lección prerequisito está completada y su evaluación aprobada para la inscripción
        if not self.leccion_prerequisito.esta_completada(inscripcion):
            return True

        return False

    def esta_completada(self, inscripcion=None):
        """Verifica si la lección está completada: todos los contenidos obligatorios vistos y todas las valoraciones de los temas aprobadas (si existen)."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[esta_completada] Lección: {self.nombre} | Inscripción: {inscripcion}")
        if not inscripcion:
            logger.info("[esta_completada] Sin inscripción, retorna False")
            return False

        contenidos = self.contenidoleccion_set.filter(obligatorio=True)
        for contenido in contenidos:
            progreso = ProgresoCapacitacion.objects.filter(
                inscripcion=inscripcion,
                contenido=contenido,
                completado=True
            ).exists()
            logger.info(f"[esta_completada] Contenido: {contenido.nombre} | Completado: {progreso}")
            if not progreso:
                logger.info(f"[esta_completada] Falta completar contenido obligatorio: {contenido.nombre}")
                return False

            # Si el contenido tiene evaluación (quiz), verificar que esté aprobada
            if hasattr(contenido, 'evaluacion'):
                quiz = getattr(contenido, 'evaluacion', None)
                if quiz:
                    aprobado = IntentoQuiz.objects.filter(
                        quiz=quiz,
                        usuario=inscripcion.empleado.usuario,
                        aprobado=True
                    ).exists()
                    logger.info(f"[esta_completada] Contenido: {contenido.nombre} | Quiz: {quiz} | Aprobado: {aprobado}")
                    if not aprobado:
                        logger.info(f"[esta_completada] Falta aprobar quiz de contenido: {contenido.nombre}")
                        return False

        # Si la lección tiene evaluación directa, también debe estar aprobada
        if hasattr(self, 'evaluacion'):
            quiz = getattr(self, 'evaluacion', None)
            if quiz:
                aprobado = IntentoQuiz.objects.filter(
                    quiz=quiz,
                    usuario=inscripcion.empleado.usuario,
                    aprobado=True
                ).exists()
                logger.info(f"[esta_completada] Evaluación directa de lección: {quiz} | Aprobado: {aprobado}")
                if not aprobado:
                    logger.info(f"[esta_completada] Falta aprobar evaluación directa de la lección")
                    return False

        logger.info(f"[esta_completada] Lección COMPLETADA: {self.nombre}")
        return True
    
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
    codigo = models.CharField(max_length=12, unique=True)
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
    def get_contenido_anterior(self):
        """Devuelve el contenido anterior en la lección según el campo orden, o None si es el primero."""
        return self.leccion.contenidoleccion_set.filter(orden__lt=self.orden).order_by('-orden').first()
    """Contenidos de una lección - MEJORADO"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_contenido = models.ForeignKey(TipoContenido, on_delete=models.CASCADE)
    
    # Archivos y URLs
    from custom_storage.media import MediaStorage
    archivo = models.FileField(
        upload_to='capacitaciones/contenido/',
        storage=MediaStorage(),
        blank=True
    )
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
        upload_to=get_certificado_externo_upload_path,
        storage=MediaStorage(),
        blank=True,
        help_text="Certificado obtenido del proveedor externo"
    )
    fecha_certificado_externo = models.DateField(null=True, blank=True)
    validado_por_admin = models.BooleanField(default=False)

    # Certificación generada automáticamente
    numero_certificado = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Identificador único del certificado (ej: CERT-2025-001)"
    )
    certificado_generado = models.FileField(
        upload_to=get_certificado_generado_upload_path,
        storage=MediaStorage(),
        null=True,
        blank=True,
        help_text="Certificado PDF generado automáticamente por el sistema"
    )
    fecha_emision_certificado = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se emitió el certificado"
    )
    
    # Observaciones
    observaciones_empleado = models.TextField(blank=True)
    observaciones_supervisor = models.TextField(blank=True)
    observaciones_admin = models.TextField(blank=True)
    
    # Usuarios relacionados
    inscrito_por = models.ForeignKey('authentication.Usuario', on_delete=models.CASCADE, related_name='inscripciones_creadas')
    aprobado_por = models.ForeignKey('authentication.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='inscripciones_aprobadas')

    # Sesión presencial concreta (null = inscripción sin sesión programada, ej. curso online)
    sesion = models.ForeignKey(
        'SesionCapacitacion', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='inscripciones',
        help_text="Convocatoria/sesión presencial específica a la que pertenece esta inscripción.",
    )

    class Meta:
        db_table = 'inscripciones_capacitacion'
        # unique compuesto por sesión: un empleado puede inscribirse al MISMO
        # curso en distintas sesiones (repetir toma, por ejemplo).
        unique_together = ['empleado', 'capacitacion', 'sesion']
        verbose_name = 'Inscripción a Capacitación'
        verbose_name_plural = 'Inscripciones a Capacitación'
        ordering = ['-fecha_inscripcion']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.capacitacion.nombre}"

    def save(self, *args, **kwargs):
        # Auto-asignar sesión cuando la capacitación es presencial/mixta y
        # se está creando la inscripción sin sesión explícita. Toma la próxima
        # sesión futura disponible (programada, con cupo); si no hay, deja la
        # inscripción "en espera" y el admin sabrá que debe crear una sesión.
        if self._state.adding and self.sesion_id is None:
            capacitacion = self.capacitacion
            if capacitacion and capacitacion.modalidad in ('presencial', 'mixta'):
                self.sesion = SesionCapacitacion.proxima_disponible_para(capacitacion)
        super().save(*args, **kwargs)

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

    @property
    def total_lecciones(self):
        """Cuenta el total de lecciones de la capacitación de esta inscripción.

        Una sola query con JOIN — más eficiente que iterar módulos y sumar.
        """
        return Leccion.objects.filter(modulo__capacitacion=self.capacitacion).count()

    def generar_numero_certificado(self):
        """Genera un número único de certificado"""
        from django.utils import timezone
        año = timezone.now().year
        # Contar certificados de esta capacitación en este año
        count = InscripcionCapacitacion.objects.filter(
            capacitacion=self.capacitacion,
            estado='aprobado',
            numero_certificado__isnull=False,
            fecha_emision_certificado__year=año
        ).count()
        self.numero_certificado = f"CERT-{año}-{self.capacitacion.codigo}-{count+1:04d}"
        return self.numero_certificado

    def puede_generar_certificado(self):
        """Verifica si cumple condiciones para generar certificado"""
        if self.estado != 'aprobado':
            return False
        # Verificar si ya tiene certificado generado
        if self.certificado_generado:
            return False
        # La capacitación decide si emite certificado (configurable por curso).
        # Para externas, el certificado lo entrega el proveedor (signal lo maneja).
        if not self.capacitacion.emite_certificado:
            return False
        # Verificar nota mínima
        if hasattr(self.capacitacion, 'plantilla_certificado'):
            plantilla = self.capacitacion.plantilla_certificado
            if self.puntaje_final and self.puntaje_final >= plantilla.nota_minima_certificado:
                return True
        return False

    def puede_descargar_certificado(self):
        """Verifica si el certificado puede ser descargado.

        Internas: necesita emite_certificado=True + número asignado (el PDF se
        renderiza al vuelo en la descarga, no se guarda archivo).
        Externas: necesita el archivo subido por el proveedor.
        """
        if self.estado != 'aprobado':
            return False
        if self.capacitacion.es_externa():
            return bool(self.certificado_externo)
        return bool(self.numero_certificado) and self.capacitacion.emite_certificado

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


class CertificadoPlantilla(models.Model):
    """Plantilla de certificado para cada capacitación"""

    capacitacion = models.OneToOneField(
        Capacitacion,
        on_delete=models.CASCADE,
        related_name='plantilla_certificado',
        help_text="Capacitación a la que pertenece esta plantilla"
    )

    # Contenido del certificado
    titulo_certificado = models.CharField(
        max_length=200,
        default="El Area de: ",
        help_text="Título principal del certificado"
    )
    texto_superior = models.TextField(
        default="Certifica que ",
        help_text="Texto que aparece antes del nombre del empleado"
    )
    texto_inferior = models.TextField(
        default="Ha completado satisfactoriamente la capacitación en: , la cual se dio de forma virtual por medio de la plataforma de SIGHU",
        help_text="Texto que aparece después del nombre del empleado"
    )

    # Elementos visuales
    logo = models.ImageField(
        upload_to=get_plantilla_logo_upload_path,
        storage=MediaStorage(),
        blank=True,
        null=True,
        help_text="Logo de la empresa (opcional)"
    )
    imagen_fondo = models.ImageField(
        upload_to=get_plantilla_fondo_upload_path,
        storage=MediaStorage(),
        blank=True,
        null=True,
        help_text="Imagen de fondo decorativa con arabescos/marcos ornamentales (opcional)"
    )
    firma_responsable = models.ImageField(
        upload_to=get_plantilla_firma_upload_path,
        storage=MediaStorage(),
        blank=True,
        null=True,
        help_text="Imagen de la firma del responsable (opcional)"
    )
    nombre_responsable = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nombre de quien firma el certificado"
    )
    cargo_responsable = models.CharField(
        max_length=200,
        blank=True,
        help_text="Cargo de quien firma el certificado (creador de la capacitación)"
    )

    # Firma de Recursos Humanos
    firma_rrhh = models.ImageField(
        upload_to=get_plantilla_firma_rrhh_upload_path,
        storage=MediaStorage(),
        blank=True,
        null=True,
        help_text="Imagen de la firma del Director de RRHH (opcional)"
    )
    nombre_rrhh = models.CharField(
        max_length=200,
        blank=True,
        default="Director de Recursos Humanos",
        help_text="Nombre del Director de RRHH"
    )
    cargo_rrhh = models.CharField(
        max_length=200,
        blank=True,
        default="Director de Recursos Humanos",
        help_text="Cargo del responsable de RRHH"
    )

    # Configuración
    incluir_calificacion = models.BooleanField(
        default=True,
        help_text="Mostrar la calificación en el certificado"
    )
    incluir_duracion = models.BooleanField(
        default=True,
        help_text="Mostrar la duración de la capacitación"
    )
    nota_minima_certificado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Nota mínima para generar el certificado automáticamente"
    )

    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        'authentication.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plantillas_certificados_creadas'
    )

    class Meta:
        db_table = 'certificados_plantillas'
        verbose_name = 'Plantilla de Certificado'
        verbose_name_plural = 'Plantillas de Certificados'

    def __str__(self):
        return f"Plantilla de certificado: {self.capacitacion.nombre}"


# =============================================================================
# CAPACITACIONES PRESENCIALES — SESIONES PROGRAMADAS
# =============================================================================

class SesionCapacitacion(models.Model):
    """Convocatoria presencial de una capacitación.

    Una misma Capacitacion puede programarse varias veces (ej: SST cada mes).
    Cada convocatoria es una SesionCapacitacion con su propia fecha, cupo,
    encargado y ventana de inscripción. Los empleados se inscriben a la sesión
    específica, no al curso abstracto.

    Estados:
      - programada: creada, aún no arranca.
      - en_curso: se pasó fecha_inicio, aún no termina.
      - finalizada: pasada fecha_fin, se cerró y calcularon aprobados.
      - cancelada: no se realizó.
    """
    MODALIDAD_CHOICES = [
        ('presencial', 'Presencial'),
        ('mixta', 'Mixta (presencial + online)'),
    ]
    ESTADO_CHOICES = [
        ('programada', 'Programada'),
        ('en_curso', 'En curso'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capacitacion = models.ForeignKey(
        Capacitacion, on_delete=models.CASCADE, related_name='sesiones',
        help_text="Capacitación (contenido) que se dicta en esta sesión.",
    )
    codigo = models.CharField(
        max_length=40,
        help_text="Código único de la convocatoria (ej: SST-2026-SEP).",
    )

    modalidad = models.CharField(max_length=15, choices=MODALIDAD_CHOICES, default='presencial')
    lugar = models.CharField(
        max_length=200,
        help_text="Aula, sede o sala virtual (ej: Aula planta Caldas).",
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)

    encargado = models.ForeignKey(
        'employees.Empleado', on_delete=models.PROTECT,
        related_name='sesiones_a_cargo',
        help_text="Empleado responsable de dictar y tomar asistencia.",
    )

    # Cupo e inscripción
    cupo_maximo = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Cupo máximo de inscritos. Null = ilimitado.",
    )
    inscripcion_abierta = models.BooleanField(
        default=False,
        help_text="Si está marcado, los empleados pueden auto-inscribirse desde el catálogo.",
    )
    ventana_inscripcion_desde = models.DateField(null=True, blank=True)
    ventana_inscripcion_hasta = models.DateField(null=True, blank=True)

    # Aprobación
    porcentaje_asistencia_minimo = models.PositiveIntegerField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="% mínimo de días asistidos para aprobar y recibir certificado.",
    )

    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='programada')
    observaciones = models.TextField(blank=True)

    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(
        'authentication.Usuario', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sesiones_creadas',
    )

    class Meta:
        db_table = 'training_sesiones_capacitacion'
        verbose_name = 'Sesión de capacitación'
        verbose_name_plural = 'Sesiones de capacitación'
        ordering = ['-fecha_inicio', 'codigo']
        constraints = [
            models.UniqueConstraint(fields=['capacitacion', 'codigo'], name='unique_capacitacion_codigo_sesion'),
        ]
        indexes = [
            models.Index(fields=['estado', 'fecha_inicio']),
            models.Index(fields=['encargado', '-fecha_inicio']),
        ]

    def __str__(self):
        return f"{self.capacitacion.nombre} — {self.codigo} ({self.fecha_inicio:%d/%m/%Y})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': 'La fecha fin no puede ser anterior a la fecha inicio.'})
        if self.ventana_inscripcion_desde and self.ventana_inscripcion_hasta:
            if self.ventana_inscripcion_hasta < self.ventana_inscripcion_desde:
                raise ValidationError({'ventana_inscripcion_hasta': 'La ventana de inscripción hasta no puede ser anterior al desde.'})

    @property
    def dias_totales(self):
        """Número de días calendario entre fecha_inicio y fecha_fin (inclusive)."""
        return (self.fecha_fin - self.fecha_inicio).days + 1

    @property
    def cupo_disponible(self):
        """Cupo disponible actual. None si es ilimitado."""
        if self.cupo_maximo is None:
            return None
        return max(0, self.cupo_maximo - self.inscripciones.count())

    def inscripcion_permitida_hoy(self):
        """True si hoy está dentro de la ventana de inscripción y hay cupo."""
        from datetime import date as _date
        hoy = _date.today()
        if not self.inscripcion_abierta:
            return False
        if self.ventana_inscripcion_desde and hoy < self.ventana_inscripcion_desde:
            return False
        if self.ventana_inscripcion_hasta and hoy > self.ventana_inscripcion_hasta:
            return False
        if self.cupo_disponible is not None and self.cupo_disponible <= 0:
            return False
        if self.estado != 'programada':
            return False
        return True

    # Ventana del link de asistencia virtual: se activa 5 min antes del
    # inicio de la sesión y sigue disponible hasta el fin de la última
    # jornada. Si no hay hora_inicio configurada se abre desde las 00:00
    # del primer día; si no hay hora_fin se cierra a las 23:59 del último.
    LINK_LEAD_MINUTES = 5

    @property
    def link_disponible_desde(self):
        from datetime import datetime, time, timedelta
        inicio = datetime.combine(self.fecha_inicio, self.hora_inicio or time.min)
        return inicio - timedelta(minutes=self.LINK_LEAD_MINUTES)

    @property
    def link_disponible_hasta(self):
        from datetime import datetime, time
        return datetime.combine(self.fecha_fin, self.hora_fin or time.max)

    def link_activo_ahora(self):
        """True si el link de reunión debe estar disponible en este momento."""
        from datetime import datetime
        ahora = datetime.now()
        return self.link_disponible_desde <= ahora <= self.link_disponible_hasta

    @classmethod
    def proxima_disponible_para(cls, capacitacion):
        """Retorna la sesión más adecuada para inscribir a un empleado ahora.

        Prioriza sesiones futuras con cupo, luego sesiones en curso, luego
        cualquier futura sin cupo (para que el admin sepa que no cupo pero
        haya visibilidad). Retorna None si no hay ninguna sesión programada.
        """
        from datetime import date as _date
        hoy = _date.today()
        candidatas = cls.objects.filter(
            capacitacion=capacitacion,
            estado__in=('programada', 'en_curso'),
        ).order_by('fecha_inicio')
        for sesion in candidatas.filter(fecha_inicio__gte=hoy):
            if sesion.cupo_disponible is None or sesion.cupo_disponible > 0:
                return sesion
        # Fallback: sesión en curso (por si el empleado se une tarde)
        en_curso = candidatas.filter(estado='en_curso', fecha_fin__gte=hoy).first()
        if en_curso is not None:
            return en_curso
        # Último recurso: la primera futura aunque esté llena, para no dejar
        # al empleado sin visibilidad de que el curso tiene programación.
        return candidatas.filter(fecha_inicio__gte=hoy).first()


class AsistenciaSesion(models.Model):
    """Asistencia de un inscrito a un día específico de una sesión.

    Un registro por (inscripcion, fecha). El encargado marca los checkboxes
    día por día. Al finalizar la sesión se calcula el % y se aprueba/reprueba.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscripcion = models.ForeignKey(
        InscripcionCapacitacion, on_delete=models.CASCADE,
        related_name='asistencias_sesion',
    )
    fecha = models.DateField(help_text="Día concreto de la sesión.")
    asistio = models.BooleanField(default=False)
    hora_llegada = models.TimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        'employees.Empleado', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='asistencias_sesion_registradas',
    )
    fecha_registro = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'training_asistencia_sesion'
        verbose_name = 'Asistencia a sesión'
        verbose_name_plural = 'Asistencias a sesiones'
        constraints = [
            models.UniqueConstraint(fields=['inscripcion', 'fecha'], name='unique_asistencia_inscripcion_fecha'),
        ]
        indexes = [
            models.Index(fields=['inscripcion', 'fecha']),
        ]
        ordering = ['fecha']

    def __str__(self):
        return f"{self.inscripcion.empleado.nombre_completo} - {self.fecha} - {'✓' if self.asistio else '✗'}"

