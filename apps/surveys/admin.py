from django.contrib import admin
from .models import (
    TipoEncuesta, Encuesta, PreguntaEncuesta, OpcionEncuesta,
    ParticipacionEncuesta, RespuestaEncuesta, EncuestaArea, EncuestaCargo
)

# =============================================================================
# TIPO DE ENCUESTA
# =============================================================================

@admin.register(TipoEncuesta)
class TipoEncuestaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'obligatoria', 'anonima', 'frecuencia_dias', 'activo')
    list_filter = ('obligatoria', 'anonima', 'activo')
    search_fields = ('codigo', 'nombre')
    ordering = ('nombre',)

# =============================================================================
# ENCUESTAS
# =============================================================================

class PreguntaEncuestaInline(admin.TabularInline):
    model = PreguntaEncuesta
    extra = 0
    fields = ('orden', 'pregunta', 'tipo_pregunta', 'categoria', 'obligatoria', 'activa')
    ordering = ['orden']
    show_change_link = True

@admin.register(Encuesta)
class EncuestaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo_encuesta', 'fecha_inicio', 'fecha_fin', 'activa', 'total_preguntas')
    list_filter = ('activa', 'tipo_encuesta', 'fecha_inicio')
    search_fields = ('codigo', 'nombre')
    date_hierarchy = 'fecha_creacion'
    inlines = [PreguntaEncuestaInline]

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'tipo_encuesta', 'descripcion', 'instrucciones')
        }),
        ('Vigencia', {
            'fields': ('fecha_inicio', 'fecha_fin', 'activa')
        }),
        ('Metadatos', {
            'fields': ('creada_por', 'fecha_creacion'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('fecha_creacion',)

    def total_preguntas(self, obj):
        return obj.preguntaencuesta_set.count()
    total_preguntas.short_description = 'Preguntas'

# =============================================================================
# PREGUNTAS Y OPCIONES
# =============================================================================

class OpcionEncuestaInline(admin.TabularInline):
    model = OpcionEncuesta
    extra = 3
    fields = ('orden', 'opcion', 'valor_numerico', 'activa')
    ordering = ['orden']

@admin.register(PreguntaEncuesta)
class PreguntaEncuestaAdmin(admin.ModelAdmin):
    list_display = ('pregunta_corta', 'encuesta', 'tipo_pregunta', 'categoria', 'orden', 'obligatoria', 'activa')
    list_filter = ('encuesta', 'tipo_pregunta', 'categoria', 'obligatoria', 'activa')
    search_fields = ('pregunta', 'categoria')
    ordering = ['encuesta', 'orden']
    inlines = [OpcionEncuestaInline]

    fieldsets = (
        ('Pregunta', {
            'fields': ('encuesta', 'tipo_pregunta', 'categoria', 'pregunta', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('orden', 'obligatoria', 'activa')
        }),
    )

    def pregunta_corta(self, obj):
        return obj.pregunta[:60] + "..." if len(obj.pregunta) > 60 else obj.pregunta
    pregunta_corta.short_description = 'Pregunta'

@admin.register(OpcionEncuesta)
class OpcionEncuestaAdmin(admin.ModelAdmin):
    list_display = ('opcion', 'pregunta_encuesta', 'valor_numerico', 'orden', 'activa')
    list_filter = ('activa', 'pregunta__encuesta')
    search_fields = ('opcion', 'pregunta__pregunta')
    ordering = ['pregunta', 'orden']

    def pregunta_encuesta(self, obj):
        return f"{obj.pregunta.encuesta.nombre} - {obj.pregunta.pregunta[:40]}..."
    pregunta_encuesta.short_description = 'Encuesta - Pregunta'

# =============================================================================
# PARTICIPACIONES Y RESPUESTAS
# =============================================================================

@admin.register(ParticipacionEncuesta)
class ParticipacionEncuestaAdmin(admin.ModelAdmin):
    list_display = ('empleado_nombre', 'encuesta', 'completada', 'porcentaje_completado', 'fecha_inicio', 'fecha_completada')
    list_filter = ('completada', 'encuesta', 'fecha_inicio')
    search_fields = ('empleado__nombre_completo', 'encuesta__nombre')
    date_hierarchy = 'fecha_inicio'
    readonly_fields = ('fecha_inicio', 'fecha_completada', 'ip_address', 'dispositivo')

    fieldsets = (
        ('Participación', {
            'fields': ('empleado', 'encuesta', 'completada', 'porcentaje_completado')
        }),
        ('Tiempo', {
            'fields': ('fecha_inicio', 'fecha_completada', 'tiempo_empleado_minutos')
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'dispositivo'),
            'classes': ('collapse',)
        }),
    )

    def empleado_nombre(self, obj):
        return obj.empleado.nombre_completo if obj.empleado else 'Anónimo'
    empleado_nombre.short_description = 'Empleado'

@admin.register(RespuestaEncuesta)
class RespuestaEncuestaAdmin(admin.ModelAdmin):
    list_display = ('participacion_info', 'pregunta_text', 'opcion_texto', 'fecha_respuesta')
    list_filter = ('participacion__encuesta', 'pregunta__tipo_pregunta')
    search_fields = ('participacion__empleado__nombre_completo', 'pregunta__pregunta')
    readonly_fields = ('fecha_respuesta',)

    def participacion_info(self, obj):
        empleado = obj.participacion.empleado.nombre_completo if obj.participacion.empleado else 'Anónimo'
        return f"{empleado} - {obj.participacion.encuesta.nombre}"
    participacion_info.short_description = 'Empleado - Encuesta'

    def pregunta_text(self, obj):
        return obj.pregunta.pregunta[:50] + "..." if len(obj.pregunta.pregunta) > 50 else obj.pregunta.pregunta
    pregunta_text.short_description = 'Pregunta'

    def opcion_texto(self, obj):
        if obj.opcion_seleccionada:
            return obj.opcion_seleccionada.opcion
        elif obj.respuesta_texto:
            return obj.respuesta_texto[:50] + "..." if len(obj.respuesta_texto) > 50 else obj.respuesta_texto
        return '-'
    opcion_texto.short_description = 'Respuesta'

# =============================================================================
# ASIGNACIONES
# =============================================================================

@admin.register(EncuestaArea)
class EncuestaAreaAdmin(admin.ModelAdmin):
    list_display = ('encuesta', 'area')
    list_filter = ('encuesta',)
    search_fields = ('encuesta__nombre', 'area__nombre')

@admin.register(EncuestaCargo)
class EncuestaCargoAdmin(admin.ModelAdmin):
    list_display = ('encuesta', 'cargo')
    list_filter = ('encuesta',)
    search_fields = ('encuesta__nombre', 'cargo__nombre')
