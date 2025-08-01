# =============================================================================
# apps/training/admin.py - CORREGIR CAPACITACIONES
# =============================================================================

from django.contrib import admin
from .models import (TipoCapacitacion, Capacitacion, CapacitacionCargo, ModuloCapacitacion, 
                     Leccion, TipoContenido, ContenidoLeccion, InscripcionCapacitacion, ProgresoCapacitacion)

@admin.register(TipoCapacitacion)
class TipoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'duracion_estimada_horas', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'tipo', 'fecha_creacion')
    search_fields = ('codigo', 'nombre')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'tipo', 'activa')
        }),
        ('Configuración', {
            'fields': ('duracion_estimada_horas', 'puntaje_aprobacion', 'intentos_maximos')
        }),
        ('Vigencia', {
            'fields': ('fecha_vigencia_inicio', 'fecha_vigencia_fin', 'version')
        }),
    )
    
    exclude = ('creada_por',)
    
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
        super().save_model(request, obj, form, change)

@admin.register(ModuloCapacitacion)
class ModuloCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'capacitacion', 'orden', 'duracion_estimada_minutos', 'activo')
    list_filter = ('activo', 'capacitacion')
    ordering = ('capacitacion', 'orden')

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
