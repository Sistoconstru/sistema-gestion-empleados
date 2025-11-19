from django.contrib import admin

# =============================================================================
# apps/evaluations/admin.py
# =============================================================================

from django.contrib import admin
from .models import (
    TipoPregunta, Valoracion, PreguntaValoracion, OpcionRespuesta, 
    IntentoValoracion, RespuestaValoracion, CertificadoCapacitacion,
    TipoEvaluacion, EvaluacionDesempeño, PreguntaEvaluacion, OpcionEvaluacion,
    AsignacionEvaluacion, RespuestaEvaluacion, ResultadoEvaluacion
)

# Registro del modelo TipoPregunta en el admin de Django
@admin.register(TipoPregunta)
class TipoPreguntaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'permite_opciones', 'permite_texto_libre')
    list_filter = ('permite_opciones', 'permite_texto_libre')

# Registro del modelo Valoracion en el admin de Django
@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacitacion', 'puntaje_maximo', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion')

# Registro del modelo TipoEvaluacion en el admin de Django
@admin.register(TipoEvaluacion)
class TipoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'dias_activacion', 'es_autoevaluacion', 'activo')
    list_filter = ('es_autoevaluacion', 'activo')

# Inline para opciones de evaluación
class OpcionEvaluacionInline(admin.TabularInline):
    model = OpcionEvaluacion
    extra = 4  # 4 opciones por defecto para escala Likert
    fields = ('opcion', 'valor_numerico', 'orden', 'activa')
    ordering = ['orden']

# Registro del modelo PreguntaEvaluacion en el admin de Django
@admin.register(PreguntaEvaluacion)
class PreguntaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('pregunta_corta', 'evaluacion', 'categoria', 'tipo_pregunta', 'peso_porcentual', 'orden', 'activa')
    list_filter = ('evaluacion', 'categoria', 'tipo_pregunta', 'activa')
    search_fields = ('pregunta', 'categoria')
    ordering = ['evaluacion', 'orden']
    inlines = [OpcionEvaluacionInline]
    
    def pregunta_corta(self, obj):
        return obj.pregunta[:60] + "..." if len(obj.pregunta) > 60 else obj.pregunta
    pregunta_corta.short_description = 'Pregunta'

# Registro del modelo OpcionEvaluacion en el admin de Django
@admin.register(OpcionEvaluacion)
class OpcionEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('opcion', 'pregunta_evaluacion', 'valor_numerico', 'orden', 'activa')
    list_filter = ('activa', 'pregunta__evaluacion')
    search_fields = ('opcion', 'pregunta__pregunta')
    ordering = ['pregunta', 'orden']
    
    def pregunta_evaluacion(self, obj):
        return f"{obj.pregunta.evaluacion.nombre} - {obj.pregunta.pregunta[:40]}..."
    pregunta_evaluacion.short_description = 'Evaluación - Pregunta'

# Inline para preguntas de evaluación en EvaluacionDesempeño
class PreguntaEvaluacionInline(admin.TabularInline):
    model = PreguntaEvaluacion
    extra = 1
    fields = ('categoria', 'pregunta', 'tipo_pregunta', 'peso_porcentual', 'orden', 'obligatoria', 'activa')
    ordering = ['orden']
    show_change_link = True  # Permite ir al detalle de la pregunta

# Registro del modelo EvaluacionDesempeño en el admin de Django
@admin.register(EvaluacionDesempeño)
class EvaluacionDesempeñoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo_evaluacion', 'activa', 'fecha_creacion', 'total_preguntas')
    list_filter = ('activa', 'tipo_evaluacion')
    search_fields = ('codigo', 'nombre')
    inlines = [PreguntaEvaluacionInline]
    
    def total_preguntas(self, obj):
        return obj.preguntaevaluacion_set.count()
    total_preguntas.short_description = 'Total Preguntas'

# Registro del modelo AsignacionEvaluacion en el admin de Django
@admin.register(AsignacionEvaluacion)
class AsignacionEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('empleado_evaluado', 'evaluacion', 'evaluador', 'estado', 'fecha_vencimiento', 'puntaje_total')
    list_filter = ('estado', 'es_autoevaluacion', 'evaluacion__tipo_evaluacion')
    search_fields = ('empleado_evaluado__nombres', 'empleado_evaluado__apellidos', 'evaluacion__nombre')
    date_hierarchy = 'fecha_asignacion'
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'completada':
            return ['empleado_evaluado', 'evaluacion', 'evaluador', 'periodo_evaluacion']
        return []

# Registro del modelo RespuestaEvaluacion en el admin de Django
@admin.register(RespuestaEvaluacion)
class RespuestaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('asignacion_info', 'pregunta_text', 'opcion_seleccionada', 'puntaje_obtenido', 'fecha_respuesta')
    list_filter = ('asignacion__evaluacion', 'pregunta__categoria')
    search_fields = ('asignacion__empleado_evaluado__nombres', 'pregunta__pregunta')
    readonly_fields = ('fecha_respuesta',)
    
    def asignacion_info(self, obj):
        return f"{obj.asignacion.empleado_evaluado.nombre_completo} - {obj.asignacion.evaluacion.nombre}"
    asignacion_info.short_description = 'Empleado - Evaluación'
    
    def pregunta_text(self, obj):
        return obj.pregunta.pregunta[:50] + "..." if len(obj.pregunta.pregunta) > 50 else obj.pregunta.pregunta
    pregunta_text.short_description = 'Pregunta'

# Registro del modelo ResultadoEvaluacion en el admin de Django
@admin.register(ResultadoEvaluacion)
class ResultadoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('asignacion_info', 'puntaje_final', 'porcentaje_obtenido', 'nivel_desempeño', 'fecha_generacion')
    list_filter = ('nivel_desempeño', 'asignacion__evaluacion__tipo_evaluacion')
    search_fields = ('asignacion__empleado_evaluado__nombres', 'asignacion__evaluacion__nombre')
    readonly_fields = ('fecha_generacion',)
    
    def asignacion_info(self, obj):
        return f"{obj.asignacion.empleado_evaluado.nombre_completo} - {obj.asignacion.evaluacion.nombre}"
    asignacion_info.short_description = 'Empleado - Evaluación'

# Registro del modelo CertificadoCapacitacion en el admin de Django
@admin.register(CertificadoCapacitacion)
class CertificadoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('numero_certificado', 'inscripcion', 'fecha_emision', 'fecha_vencimiento')
    search_fields = ('numero_certificado',)
