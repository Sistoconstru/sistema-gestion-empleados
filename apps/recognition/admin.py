from django.contrib import admin

# Register your models here.

# =============================================================================
# apps/recognition/admin.py
# =============================================================================

from django.contrib import admin
from .models import (TipoActividad, HistorialPuntos, TipoReconocimiento, Reconocimiento,
                     TipoInsignia, InsigniaEmpleado, TipoBeneficio, CanjeoBeneficio)

@admin.register(TipoActividad)
class TipoActividadAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'puntos_base', 'multiplicador_complejidad', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre', 'descripcion')
    list_editable = ('puntos_base', 'multiplicador_complejidad', 'activo')
    ordering = ('nombre',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Configuración de Puntos', {
            'fields': ('puntos_base', 'multiplicador_complejidad'),
            'description': 'Configure los puntos base y multiplicador. Para asignación manual, deje puntos_base en 0.'
        }),
        ('Estado', {
            'fields': ('activo',),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.codigo in ['MANUAL_ADMIN']:  # Proteger tipos críticos
            return ('codigo',)
        return ()
    
    class Meta:
        verbose_name = 'Tipo de Actividad'
        verbose_name_plural = 'Tipos de Actividad'

@admin.register(HistorialPuntos)
class HistorialPuntosAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tipo_actividad', 'puntos', 'fecha_obtencion', 'validado')
    list_filter = ('validado', 'tipo_actividad', 'fecha_obtencion')

@admin.register(TipoReconocimiento)
class TipoReconocimientoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'periodicidad', 'permite_repetir_empleado', 'activo')
    list_filter = ('periodicidad', 'activo')

@admin.register(Reconocimiento)
class ReconocimientoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'tipo_reconocimiento', 'periodo', 'año', 'puntuacion_obtenida')
    list_filter = ('tipo_reconocimiento', 'año', 'periodo')

@admin.register(TipoInsignia)
class TipoInsigniaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'nivel', 'puntos_requeridos', 'activa')
    list_filter = ('nivel', 'activa')

@admin.register(TipoBeneficio)
class TipoBeneficioAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'costo_puntos', 'stock_actual', 'disponible')
    list_filter = ('categoria', 'disponible')
