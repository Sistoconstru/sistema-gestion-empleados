# =============================================================================
# apps/training/admin.py - CORREGIR CAPACITACIONES
# =============================================================================

from django.contrib import admin
from .models import (TipoCapacitacion, Capacitacion, CapacitacionCargo, ModuloCapacitacion, 
                     Leccion, TipoContenido, ContenidoLeccion, InscripcionCapacitacion, ProgresoCapacitacion,
                     QuizLeccion, PreguntaQuiz, OpcionPreguntaQuiz, IntentoQuiz, RespuestaQuiz)

@admin.register(TipoCapacitacion)
class TipoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'es_externa_display', 'duracion_estimada_horas', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'tipo', 'es_capacitacion_externa', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'nombre_proveedor')

    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'tipo', 'activa', 'nivel_dificultad')
        }),
        ('Capacitación Externa', {
            'fields': ('es_capacitacion_externa', 'nombre_proveedor', 'url_curso_externo', 'requiere_certificado_externo'),
            'description': 'Marcar "Es capacitación externa" si es ofrecida por un proveedor externo (Coursera, Udemy, etc.). Esto simplifica la gestión: solo necesitas la URL del curso.',
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('duracion_estimada_horas', 'puntaje_aprobacion', 'intentos_maximos', 'puntos_gamificacion', 'costo_inscripcion')
        }),
        ('Vigencia', {
            'fields': ('fecha_vigencia_inicio', 'fecha_vigencia_fin', 'version')
        }),
        ('Opciones Avanzadas', {
            'fields': ('visible_en_catalogo', 'permite_certificacion_manual', 'requiere_prerequisitos'),
            'classes': ('collapse',)
        }),
    )

    exclude = ('creada_por', 'proveedor_externo', 'url_inscripcion_externa', 'permite_autocompletado')

    def es_externa_display(self, obj):
        """Muestra si es externa con ícono"""
        if obj.es_externa():
            return '🌐 Externa'
        return '📚 Interna'
    es_externa_display.short_description = 'Tipo'

    def save_model(self, request, obj, form, change):
        # Asigna el usuario que crea la capacitación solo al crear
        if not change:
            obj.creada_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(CapacitacionCargo)
class CapacitacionCargoAdmin(admin.ModelAdmin):
    list_display = ('capacitacion', 'cargo', 'obligatoria', 'dias_plazo_completar')
    list_filter = ('obligatoria',)
    
    exclude = ('asignado_por',)
    
    def save_model(self, request, obj, form, change):
        # Asigna el usuario que realiza la asignación solo al crear
        if not change:
            obj.asignado_por = request.user

class OpcionPreguntaQuizInline(admin.TabularInline):
    model = OpcionPreguntaQuiz
    extra = 4  # Número de opciones vacías a mostrar
    fields = ('texto', 'es_correcta', 'retroalimentacion', 'orden')

class PreguntaQuizInline(admin.StackedInline):
    model = PreguntaQuiz
    extra = 1
    fields = ('texto', 'tipo', 'puntaje', 'imagen', 'explicacion', 'orden')
    
@admin.register(QuizLeccion)
class QuizLeccionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'leccion', 'porcentaje_aprobacion', 'intentos_maximos', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'porcentaje_aprobacion')
    search_fields = ('titulo', 'descripcion', 'leccion__nombre')
    inlines = [PreguntaQuizInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('leccion', 'titulo', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('porcentaje_aprobacion', 'tiempo_limite', 'intentos_maximos')
        }),
    )

@admin.register(PreguntaQuiz)
class PreguntaQuizAdmin(admin.ModelAdmin):
    list_display = ('texto_corto', 'quiz', 'tipo', 'puntaje', 'orden')
    list_filter = ('tipo', 'quiz')
    search_fields = ('texto', 'explicacion')
    inlines = [OpcionPreguntaQuizInline]
    
    def texto_corto(self, obj):
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    texto_corto.short_description = 'Pregunta'

@admin.register(IntentoQuiz)
class IntentoQuizAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'quiz', 'fecha_inicio', 'puntaje_obtenido', 'aprobado')
    list_filter = ('aprobado', 'fecha_inicio')
    search_fields = ('usuario__username', 'quiz__titulo')
    readonly_fields = ('fecha_inicio', 'fecha_fin', 'puntaje_obtenido', 'tiempo_utilizado', 'aprobado')

@admin.register(RespuestaQuiz)
class RespuestaQuizAdmin(admin.ModelAdmin):
    list_display = ('intento', 'pregunta', 'es_correcta', 'fecha_respuesta')
    list_filter = ('es_correcta', 'fecha_respuesta')
    search_fields = ('intento__usuario__username', 'pregunta__texto')
    readonly_fields = ('intento', 'pregunta', 'opcion_seleccionada', 'es_correcta', 'fecha_respuesta')

@admin.register(ModuloCapacitacion)
class ModuloCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'capacitacion', 'orden', 'duracion_estimada_minutos', 'activo', 'modulo_prerequisito')
    list_filter = ('activo', 'capacitacion')
    ordering = ('capacitacion', 'orden')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "modulo_prerequisito":
            # Excluir el módulo actual de la lista de prerequisitos
            if request.resolver_match.kwargs.get('object_id'):
                kwargs["queryset"] = ModuloCapacitacion.objects.exclude(
                    id=request.resolver_match.kwargs['object_id']
                )
            # Añadir "--------" como opción para indicar "sin prerequisito"
            kwargs["empty_label"] = "--------"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Leccion)
class LeccionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'modulo', 'orden', 'duracion_estimada_minutos', 'activa')
    list_filter = ('activa', 'modulo__capacitacion')
    ordering = ('modulo', 'orden')

@admin.register(TipoContenido)
class TipoContenidoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'requiere_archivo', 'requiere_url')
    list_filter = ('requiere_archivo', 'requiere_url')

@admin.register(ContenidoLeccion)
class ContenidoLeccionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'leccion', 'tipo_contenido', 'orden', 'obligatorio')
    list_filter = ('tipo_contenido', 'obligatorio')
    ordering = ('leccion', 'orden')

@admin.register(InscripcionCapacitacion)
class InscripcionCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'capacitacion', 'estado', 'obligatoria', 'fecha_inscripcion', 'puntaje_final')
    list_filter = ('estado', 'obligatoria', 'fecha_inscripcion')
    search_fields = ('empleado__nombres', 'empleado__apellidos', 'capacitacion__nombre')
    
    exclude = ('inscrito_por',)
    
    def save_model(self, request, obj, form, change):
        # Asigna el usuario que inscribe solo al crear
        if not change:
            obj.inscrito_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(ProgresoCapacitacion)
class ProgresoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('inscripcion', 'contenido', 'completado', 'porcentaje_visto', 'numero_visitas')
    list_filter = ('completado',)
