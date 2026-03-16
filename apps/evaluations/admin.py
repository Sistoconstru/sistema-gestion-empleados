from django.contrib import admin

# =============================================================================
# apps/evaluations/admin.py
# =============================================================================

from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from django import forms
from datetime import datetime
from .models import (
    TipoPregunta, Valoracion, PreguntaValoracion, OpcionRespuesta,
    IntentoValoracion, RespuestaValoracion, CertificadoCapacitacion,
    TipoEvaluacion, EvaluacionDesempeño, PreguntaEvaluacion, OpcionEvaluacion,
    AsignacionEvaluacion, RespuestaEvaluacion, ResultadoEvaluacion,
    PlanMejoraPredefinido, SeguimientoBimensual, EvaluacionFinal, EvaluacionCargo
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


# ===================== ADMIN PARA PLANES PREDEFINIDOS =====================

# Inline para seguimientos bimensuales
class SeguimientoBimensualInline(admin.TabularInline):
    model = SeguimientoBimensual
    extra = 0
    fields = ('numero_bimestre', 'fecha_limite', 'estado', 'avance_satisfactorio', 'fecha_completado')
    readonly_fields = ('fecha_limite',)
    ordering = ['numero_bimestre']

# Registro del modelo PlanMejoraPredefinido en el admin de Django
@admin.register(PlanMejoraPredefinido)
class PlanMejoraPredefinidoAdmin(admin.ModelAdmin):
    list_display = ('empleado_name', 'estado', 'fecha_creacion', 'fecha_aprobacion', 'generado_por')
    list_filter = ('estado', 'fecha_creacion', 'generado_por')
    search_fields = (
        'asignacion_evaluacion__empleado_evaluado__nombres',
        'asignacion_evaluacion__empleado_evaluado__apellidos',
    )
    readonly_fields = ('fecha_creacion', 'fecha_aprobacion')
    inlines = [SeguimientoBimensualInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('asignacion_evaluacion', 'estado', 'fecha_creacion', 'fecha_aprobacion')
        }),
        ('Plan de Mejora', {
            'fields': ('plan_mejora',),
            'classes': ('wide',)
        }),
        ('Usuarios Involucrados', {
            'fields': ('generado_por', 'aprobado_por')
        }),
        ('Comentarios', {
            'fields': ('comentarios_aprobacion', 'comentarios_seguimiento'),
            'classes': ('collapse',)
        }),
    )
    
    def empleado_name(self, obj):
        return obj.asignacion_evaluacion.empleado_evaluado.get_full_name()
    empleado_name.short_description = 'Empleado'


# Registro del modelo SeguimientoBimensual en el admin de Django
@admin.register(SeguimientoBimensual)
class SeguimientoBimensualAdmin(admin.ModelAdmin):
    list_display = ('plan_empleado', 'numero_bimestre', 'fecha_limite', 'estado', 'avance_satisfactorio', 'fecha_completado')
    list_filter = ('estado', 'numero_bimestre', 'avance_satisfactorio', 'fecha_limite')
    search_fields = (
        'plan_mejora__asignacion_evaluacion__empleado_evaluado__nombres',
        'plan_mejora__asignacion_evaluacion__empleado_evaluado__apellidos',
    )
    readonly_fields = ('fecha_completado',)
    
    fieldsets = (
        ('Información del Seguimiento', {
            'fields': ('plan_mejora', 'numero_bimestre', 'fecha_limite', 'estado')
        }),
        ('Resultados del Seguimiento', {
            'fields': ('avance_satisfactorio', 'observaciones', 'fecha_completado', 'completado_por')
        }),
    )
    
    def plan_empleado(self, obj):
        return f"{obj.plan_mejora.asignacion_evaluacion.empleado_evaluado.get_full_name()} - {obj.numero_bimestre}°"
    plan_empleado.short_description = 'Empleado - Bimestre'


# Registro del modelo EvaluacionFinal en el admin de Django
@admin.register(EvaluacionFinal)
class EvaluacionFinalAdmin(admin.ModelAdmin):
    list_display = ('plan_empleado', 'resultado', 'fecha_evaluacion', 'evaluado_por')
    list_filter = ('resultado', 'fecha_evaluacion', 'evaluado_por')
    search_fields = (
        'plan_mejora__asignacion_evaluacion__empleado_evaluado__nombres',
        'plan_mejora__asignacion_evaluacion__empleado_evaluado__apellidos',
    )
    readonly_fields = ('fecha_evaluacion',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('plan_mejora', 'resultado', 'fecha_evaluacion', 'evaluado_por')
        }),
        ('Conclusión', {
            'fields': ('conclusion',),
            'classes': ('wide',)
        }),
    )
    
    def plan_empleado(self, obj):
        return obj.plan_mejora.asignacion_evaluacion.empleado_evaluado.get_full_name()
    plan_empleado.short_description = 'Empleado'

# =============================================================================
# Admin de EvaluacionCargo con control de activación
# =============================================================================

@admin.register(EvaluacionCargo)
class EvaluacionCargoAdmin(admin.ModelAdmin):
    list_display = ('evaluacion', 'cargo', 'estado_badge', 'fecha_asignacion', 'fecha_vencimiento_planeada', 'fecha_activacion', 'asignado_por')
    list_filter = ('estado', 'evaluacion__tipo_evaluacion', 'fecha_asignacion')
    search_fields = ('evaluacion__nombre', 'cargo__nombre')
    date_hierarchy = 'fecha_asignacion'
    actions = ['activar_evaluaciones', 'finalizar_evaluaciones']
    
    readonly_fields = ('fecha_asignacion', 'fecha_activacion', 'activada_por')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('evaluacion', 'cargo', 'estado', 'asignado_por', 'fecha_asignacion')
        }),
        ('Control de Activación', {
            'fields': ('fecha_vencimiento_planeada', 'dias_para_completar', 'fecha_activacion', 'activada_por'),
            'description': 'Configure la fecha de vencimiento antes de activar. Las asignaciones a empleados se crean al activar.'
        }),
    )
    
    def estado_badge(self, obj):
        colores = {
            'programada': '#ffc107',  # Amarillo
            'activa': '#28a745',       # Verde
            'finalizada': '#6c757d'    # Gris
        }
        color = colores.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def activar_evaluaciones(self, request, queryset):
        """
        Acción para activar evaluaciones programadas.
        Abre una página intermedia para especificar fecha de vencimiento.
        """
        # Filtrar solo las que están en estado 'programada'
        evaluaciones_programadas = queryset.filter(estado='programada')
        
        if not evaluaciones_programadas.exists():
            self.message_user(
                request,
                "No hay evaluaciones en estado 'Programada' en la selección.",
                level=messages.WARNING
            )
            return
        
        # Guardar los IDs en la sesión para la página intermedia
        request.session['evaluaciones_a_activar'] = list(evaluaciones_programadas.values_list('id', flat=True))

        # Redirigir a página intermedia (formulario)
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse('evaluations:activar_evaluaciones_form'))
    
    activar_evaluaciones.short_description = "✅ Activar evaluaciones seleccionadas"
    
    def finalizar_evaluaciones(self, request, queryset):
        """Marca evaluaciones activas como finalizadas"""
        count = queryset.filter(estado='activa').update(estado='finalizada')
        self.message_user(
            request,
            f"{count} evaluación(es) marcada(s) como finalizada(s).",
            level=messages.SUCCESS if count > 0 else messages.WARNING
        )
    
    finalizar_evaluaciones.short_description = "🏁 Finalizar evaluaciones seleccionadas"
    
    def get_readonly_fields(self, request, obj=None):
        """No permitir editar una vez activada"""
        if obj and obj.estado in ['activa', 'finalizada']:
            return self.readonly_fields + ('evaluacion', 'cargo', 'estado', 'fecha_vencimiento_planeada', 'dias_para_completar')
        return self.readonly_fields


# Necesitamos importar format_html para los badges
from django.utils.html import format_html
