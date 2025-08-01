# =============================================================================
# apps/core/admin.py
# =============================================================================

from django.contrib import admin
from .models import ConfiguracionSistema, LogActividad

# Registro del modelo ConfiguracionSistema en el admin de Django
@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista de configuraciones
    list_display = ('modulo', 'clave', 'tipo_dato', 'editable_usuario', 'fecha_actualizacion')
    # Filtros disponibles en la barra lateral
    list_filter = ('modulo', 'tipo_dato', 'editable_usuario')
    # Campos por los que se puede buscar
    search_fields = ('modulo', 'clave', 'descripcion')
    
    # Agrupación de campos en el formulario de edición
    fieldsets = (
        ('Configuración', {
            'fields': ('modulo', 'clave', 'valor', 'tipo_dato')
        }),
        ('Información Adicional', {
            'fields': ('descripcion', 'valor_defecto', 'editable_usuario')
        }),
    )

# Registro del modelo LogActividad en el admin de Django
@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista de logs
    list_display = ('usuario', 'accion', 'modelo', 'ip_address', 'fecha_accion')
    # Filtros disponibles en la barra lateral
    list_filter = ('accion', 'modelo', 'fecha_accion')
    # Campos por los que se puede buscar
    search_fields = ('usuario__username', 'modelo', 'accion')
    # Campos que serán solo de lectura
    readonly_fields = ('fecha_accion',)
    
    def has_add_permission(self, request):
        return False  # No permitir agregar logs manualmente

